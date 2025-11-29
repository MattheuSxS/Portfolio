# # retrain.py
# import time
# import schedule
# from datetime import datetime
# from sales_forecaster import SalesForecastingPipeline

# def scheduled_retraining():
#     """Função para retreinamento agendado"""
#     print(f"Iniciando retreinamento em {datetime.now()}")
    
#     try:
#         pipeline = SalesForecastingPipeline()
#         pipeline.run_training(periods=30)
#         print("Retreinamento concluído com sucesso!")
#     except Exception as e:
#         print(f"Erro no retreinamento: {e}")

# # Agendar execuções
# schedule.every().day.at("02:00").do(scheduled_retraining)  # Diário às 2h
# schedule.every().sunday.at("03:00").do(scheduled_retraining)  # Semanal adicional

# if __name__ == "__main__":
#     print("Agendador de retreinamento iniciado...")
#     while True:
#         schedule.run_pending()
#         time.sleep(60)