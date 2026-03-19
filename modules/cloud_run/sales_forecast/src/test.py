# sales_forecaster.py
from google.cloud import bigquery
import pandas as pd
import numpy as np
from prophet import Prophet
from prophet.serialize import model_to_json, model_from_json
from prophet.diagnostics import cross_validation, performance_metrics
import pickle
import warnings
warnings.filterwarnings('ignore')

class ProphetSalesForecaster:
    def __init__(self):
        self.client = bigquery.Client()
        self.models = {}
        self.forecasts = {}
        self.performance_metrics = {}

    def fetch_sales_data(self):
        """Busca dados históricos completos do BigQuery"""
        query = """
        SELECT
            SUM(TBSS.discount_applied) AS discount_applied,
            SUM(TBSS.final_price) AS final_price,
            TBSS.region,
            TBAS.state,
            TBSS.order_status,
            FORMAT_TIMESTAMP('%Y-%m-%d', TBSS.purchase_date) AS purchase_date
        FROM
            `gcp-default-portfolio.ls_customers.tb_sales` AS TBSS
        INNER JOIN
            `gcp-default-portfolio.ls_customers.tb_address` AS TBAS
        ON
            TBSS.associate_id = TBAS.fk_associate_id
            AND TBSS.order_status = "completed"
        GROUP BY
            TBSS.region,
            TBAS.state,
            TBSS.order_status,
            FORMAT_TIMESTAMP('%Y-%m-%d', TBSS.purchase_date)
        """
        
        print("Buscando dados históricos completos do BigQuery...")
        df = self.client.query(query).to_dataframe()
        print(f"Dados carregados: {len(df)} registros")
        return df
    
    def prepare_data_for_prophet(self, df, group_by=None):
        """
        Prepara dados para o Prophet
        group_by: None para dados agregados, ou ['region', 'state'] para grupos específicos
        """
        if group_by:
            groups = df.groupby(group_by)
        else:
            groups = [('total', df)]
        
        prophet_data = {}
        
        for group_name, group_df in groups:
            # Agregar por data
            daily_sales = group_df.groupby('purchase_date').agg({
                'final_price': 'sum',
                'discount_applied': 'sum'
            }).reset_index()
            
            # Preparar formato do Prophet
            prophet_df = daily_sales[['purchase_date', 'final_price']].copy()
            prophet_df.columns = ['ds', 'y']
            prophet_df['ds'] = pd.to_datetime(prophet_df['ds'])
            prophet_df = prophet_df.sort_values('ds')
            
            # Adicionar regressor de desconto
            discount_data = daily_sales[['purchase_date', 'discount_applied']].copy()
            discount_data.columns = ['ds', 'discount']
            discount_data['ds'] = pd.to_datetime(discount_data['ds'])
            
            prophet_df = prophet_df.merge(discount_data, on='ds', how='left')
            prophet_df['discount'] = prophet_df['discount'].fillna(0)
            
            prophet_data[group_name] = prophet_df
        
        return prophet_data
    
    def train_prophet_models(self, df, group_by=None, periods=30):
        """Treina modelos Prophet para diferentes agrupamentos"""
        print("Preparando dados para o Prophet...")
        prophet_data = self.prepare_data_for_prophet(df, group_by)
        
        for group_name, data_df in prophet_data.items():
            if len(data_df) < 10:  # Mínimo de pontos para treinar
                print(f"Dados insuficientes para {group_name}, pulando...")
                continue
                
            print(f"Treinando modelo para: {group_name}")
            
            # Configurar modelo Prophet com dados históricos completos
            model = Prophet(
                daily_seasonality=False,
                weekly_seasonality=True,
                yearly_seasonality=True,
                changepoint_prior_scale=0.05,
                seasonality_prior_scale=10.0,
                holidays_prior_scale=10.0
            )
            
            # Adicionar regressor de desconto
            model.add_regressor('discount')
            
            # Adicionar feriados brasileiros
            try:
                model.add_country_holidays(country_name='BR')
                print(f"  ✅ Feriados brasileiros adicionados para {group_name}")
            except:
                print(f"  ⚠️  Não foi possível adicionar feriados para {group_name}")
            
            # Treinar modelo
            model.fit(data_df)
            
            # Fazer previsão
            future = model.make_future_dataframe(periods=periods)
            
            # Adicionar regressores para o futuro (usando média dos últimos 30 dias)
            last_discount = data_df['discount'].tail(30).mean()
            future['discount'] = last_discount
            
            forecast = model.predict(future)
            
            # Calcular métricas de performance
            try:
                df_cv = cross_validation(
                    model, 
                    initial='365 days', 
                    period='180 days', 
                    horizon='90 days',
                    parallel="processes"
                )
                df_p = performance_metrics(df_cv)
                self.performance_metrics[group_name] = {
                    'mse': df_p['mse'].mean(),
                    'rmse': df_p['rmse'].mean(),
                    'mae': df_p['mae'].mean(),
                    'mape': df_p['mape'].mean()
                }
            except Exception as e:
                print(f"  ⚠️  Erro na validação cruzada para {group_name}: {e}")
                self.performance_metrics[group_name] = None
            
            self.models[group_name] = model
            self.forecasts[group_name] = forecast
            
            print(f"  ✅ Modelo treinado para {group_name} - {len(data_df)} pontos de dados")
        
        return self.models, self.forecasts
    
    def save_models(self, filepath='/Users/terr0xs/Documents/github/Portfolio/src/cloud_run/sales_forecast/models/prophet_models.pkl'):
        """Salva os modelos treinados usando serialização nativa do Prophet"""
        try:
            # Preparar dados para serialização
            models_serialized = {}
            forecasts_serialized = {}
            
            # Serializar cada modelo usando o método nativo do Prophet
            for group_name, model in self.models.items():
                # Converter modelo Prophet para JSON
                models_serialized[group_name] = model_to_json(model)
                
                # Serializar forecast (DataFrame)
                if group_name in self.forecasts:
                    forecasts_serialized[group_name] = self.forecasts[group_name].to_dict()
            
            # Criar objeto completo para salvar
            data_to_save = {
                'models_serialized': models_serialized,
                'forecasts_serialized': forecasts_serialized,
                'performance_metrics': self.performance_metrics
            }
            
            # Salvar usando pickle
            with open(filepath, 'wb') as f:
                pickle.dump(data_to_save, f)
            
            print(f"✅ Modelos salvos com sucesso em {filepath}")
            print(f"   - {len(models_serialized)} modelos serializados")
            print(f"   - {len(forecasts_serialized)} forecasts salvos")
            
        except Exception as e:
            print(f"❌ Erro ao salvar modelos: {e}")
            raise
    
    def load_models(self, filepath='/Users/terr0xs/Documents/github/Portfolio/src/cloud_run/sales_forecast/models/prophet_models.pkl'):
        """Carrega modelos salvos usando desserialização nativa do Prophet"""
        try:
            with open(filepath, 'rb') as f:
                loaded_data = pickle.load(f)
            
            # Desserializar modelos
            models_serialized = loaded_data['models_serialized']
            self.models = {}
            
            for group_name, model_json in models_serialized.items():
                self.models[group_name] = model_from_json(model_json)
            
            # Desserializar forecasts
            forecasts_serialized = loaded_data.get('forecasts_serialized', {})
            self.forecasts = {}
            
            for group_name, forecast_dict in forecasts_serialized.items():
                self.forecasts[group_name] = pd.DataFrame(forecast_dict)
            
            # Carregar métricas de performance
            self.performance_metrics = loaded_data.get('performance_metrics', {})
            
            print(f"✅ Modelos carregados com sucesso de {filepath}")
            print(f"   - {len(self.models)} modelos carregados")
            print(f"   - {len(self.forecasts)} forecasts carregados")
            
        except Exception as e:
            print(f"❌ Erro ao carregar modelos: {e}")
            raise
    
    def get_forecast_dataframe(self, group_name='total', include_components=False):
        """Retorna DataFrame com previsões para uso no Streamlit"""
        if group_name not in self.forecasts:
            return None
        
        forecast = self.forecasts[group_name].copy()
        
        # Selecionar colunas principais
        result_cols = ['ds', 'yhat', 'yhat_lower', 'yhat_upper']
        
        if include_components:
            # Adicionar componentes sazonais
            component_cols = [col for col in forecast.columns if 'weekly' in col or 'yearly' in col or 'trend' in col]
            result_cols.extend(component_cols)
        
        return forecast[result_cols]
    
    def get_historical_data(self, group_name='total'):
        """Retorna dados históricos para o grupo especificado"""
        if group_name not in self.models:
            return None
        return self.models[group_name].history
    
    def get_performance_metrics(self, group_name='total'):
        """Retorna métricas de performance"""
        return self.performance_metrics.get(group_name)
    
    def get_forecast_summary(self, group_name='total', last_n_days=7):
        """Retorna resumo das previsões para o Streamlit"""
        if group_name not in self.forecasts:
            return None
        
        forecast = self.forecasts[group_name]
        historical = self.get_historical_data(group_name)
        
        # Última data histórica
        last_historical_date = historical['ds'].max()
        
        # Previsões futuras (após a última data histórica)
        future_forecast = forecast[forecast['ds'] > last_historical_date]
        
        # Últimas previsões
        last_forecasts = future_forecast.tail(last_n_days)
        
        summary = {
            'group_name': group_name,
            'last_historical_date': last_historical_date,
            'historical_data_points': len(historical),
            'forecast_periods': len(future_forecast),
            'performance_metrics': self.get_performance_metrics(group_name),
            'recent_forecasts': last_forecasts[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_dict('records'),
            'total_forecast_30d': future_forecast['yhat'].sum() if len(future_forecast) > 0 else 0
        }
        
        return summary
    
    def get_available_groups(self):
        """Retorna lista de grupos disponíveis"""
        return list(self.models.keys())

# Pipeline atualizado
class SalesForecastingPipeline:
    def __init__(self):
        self.forecaster = ProphetSalesForecaster()
    
    def run_training(self, periods=30, group_by=None):
        """Executa treinamento completo"""
        # Buscar dados
        df = self.forecaster.fetch_sales_data()
        
        if df.empty:
            print("Nenhum dado encontrado!")
            return None
        
        print("Iniciando treinamento dos modelos...")
        
        # Treinar modelos
        models, forecasts = self.forecaster.train_prophet_models(
            df, 
            group_by=group_by,
            periods=periods
        )
        
        # Salvar modelos
        self.forecaster.save_models()
        
        print(f"✅ Treinamento concluído! {len(models)} modelos criados e salvos.")
        
        return self.forecaster
    
    def load_existing_models(self):
        """Carrega modelos existentes"""
        self.forecaster.load_models()
        return self.forecaster


class StreamlitHelper:
    """Classe auxiliar para integração com Streamlit"""
    
    @staticmethod
    def prepare_forecast_chart_data(forecaster, group_name='total'):
        """Prepara dados para gráficos no Streamlit"""
        historical = forecaster.get_historical_data(group_name)
        forecast = forecaster.get_forecast_dataframe(group_name)
        
        if historical is None or forecast is None:
            return None
        
        # Combinar dados históricos e previsões
        historical_chart = historical[['ds', 'y']].rename(columns={'y': 'Vendas Reais'})
        forecast_chart = forecast[['ds', 'yhat']].rename(columns={'yhat': 'Vendas Previstas'})
        
        # Identificar período de previsão
        last_historical_date = historical['ds'].max()
        historical_forecast = forecast[forecast['ds'] <= last_historical_date]
        future_forecast = forecast[forecast['ds'] > last_historical_date]
        
        return {
            'historical': historical_chart,
            'forecast': forecast_chart,
            'historical_forecast': historical_forecast,
            'future_forecast': future_forecast,
            'last_historical_date': last_historical_date
        }
    
    @staticmethod
    def get_metrics_display(metrics):
        """Formata métricas para display no Streamlit"""
        if not metrics:
            return "Métricas não disponíveis"
        
        return f"""
        **MSE**: {metrics['mse']:.2f}  
        **RMSE**: {metrics['rmse']:.2f}  
        **MAE**: {metrics['mae']:.2f}  
        **MAPE**: {metrics['mape']:.2%}
        """

# Teste da função de salvamento
if __name__ == "__main__":
    # Teste rápido
    pipeline = SalesForecastingPipeline()
    
    # Tentar carregar modelos existentes primeiro
    try:
        forecaster = pipeline.load_existing_models()
        print("✅ Modelos carregados com sucesso!")
    except:
        print("ℹ️  Nenhum modelo existente encontrado. Execute o treinamento primeiro.")