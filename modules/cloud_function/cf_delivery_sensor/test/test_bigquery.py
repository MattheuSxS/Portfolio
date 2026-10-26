#TODO: I HAVE TO FIX THE IMPORT PATH BELOW
# modules/cloud_function/cf_customers/test/test_bigquery.py
import pytest
import json
import io
from unittest.mock import Mock, patch, MagicMock, call
import logging
from google.cloud import bigquery
from google.cloud.exceptions import GoogleCloudError
from modules.cloud_function.cf_delivery_sensor.src.utils.bigquery import BigQuery

# # Import corrigido considerando sua estrutura
# try:
#     from src.utils.bigquery import BigQuery
# except ImportError:
#     import sys
#     from pathlib import Path
#     sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
#     from utils.bigquery import BigQuery


class TestBigQueryInit:
    """Testes para o método __init__ da classe BigQuery"""
    
    @patch('modules.cloud_function.cf_delivery_sensor.src.utils.bigquery.bigquery.Client')
    def test_init_with_project_id(self, mock_client_class):
        """Testa inicialização com project ID"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        project_id = "test-project-123"
        bq = BigQuery(project=project_id)
        
        assert bq.project == project_id
        mock_client_class.assert_called_once_with(project_id)
        assert bq.client == mock_client
    
    @patch('modules.cloud_function.cf_delivery_sensor.src.utils.bigquery.bigquery.Client')
    def test_init_without_project_id(self, mock_client_class):
        """Testa inicialização sem project ID (deve usar default)"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        bq = BigQuery(project="")
        
        # BigQuery Client sem project usa o projeto padrão do ambiente
        mock_client_class.assert_called_once_with("")
        assert bq.project == ""


class TestBatchLoadFromMemory:
    """Testes para o método batch_load_from_memory"""
    
    @pytest.fixture
    def mock_bigquery_client(self):
        """Fixture that returns a mock of the BigQuery client"""
        with patch('modules.cloud_function.cf_delivery_sensor.src.utils.bigquery.bigquery.Client') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            yield mock_client
    
    @pytest.fixture
    def sample_data(self):
        """Dados de exemplo para testes"""
        return [
            {"id": 1, "name": "Test 1", "value": 100},
            {"id": 2, "name": "Test 2", "value": 200},
            {"id": 3, "name": "Test 3", "value": 300}
        ]
    
    def test_batch_load_success(self, mock_bigquery_client, sample_data, caplog):
        """Testa carregamento bem-sucedido de dados"""
        # Setup
        mock_load_job = Mock()
        mock_load_job.output_rows = len(sample_data)
        mock_load_job.result = Mock()
        
        mock_bigquery_client.load_table_from_file.return_value = mock_load_job
        
        # Execute
        bq = BigQuery(project="test-project")
        bq.client = mock_bigquery_client
        
        with caplog.at_level(logging.INFO):
            bq.batch_load_from_memory(
                data=sample_data,
                dataset="test_dataset",
                table="test_table"
            )
        
        # Verify
        expected_table_id = "test-project.test_dataset.test_table"
        
        # Verifica que o job config foi criado corretamente
        call_args = mock_bigquery_client.load_table_from_file.call_args
        assert call_args is not None
        
        # Verifica o arquivo em memória
        memory_file = call_args[0][0]
        assert isinstance(memory_file, io.BytesIO)
        
        # Verifica o conteúdo do arquivo
        memory_file.seek(0)
        lines = memory_file.read().decode('utf-8').strip().split('\n')
        assert len(lines) == len(sample_data)
        
        for i, line in enumerate(lines):
            loaded_data = json.loads(line)
            assert loaded_data == sample_data[i]
        
        # Verifica a tabela de destino
        assert call_args[0][1] == expected_table_id
        
        # Verifica job config
        job_config = call_args[1]['job_config']
        assert job_config.source_format == bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
        assert job_config.write_disposition == bigquery.WriteDisposition.WRITE_APPEND
        assert job_config.create_disposition == bigquery.CreateDisposition.CREATE_NEVER
        assert job_config.autodetect is False
        
        # Verifica que o job foi executado
        mock_load_job.result.assert_called_once()
        
        # Verifica logs
        assert f"Starting batch load to {expected_table_id}..." in caplog.text
        assert f"batch load was successful. {len(sample_data)} rows loaded into {expected_table_id}." in caplog.text
    
    def test_batch_load_empty_data(self, mock_bigquery_client, caplog):
        """Testa carregamento com lista vazia"""
        mock_load_job = Mock()
        mock_load_job.output_rows = 0
        mock_load_job.result = Mock()
        
        mock_bigquery_client.load_table_from_file.return_value = mock_load_job
        
        bq = BigQuery(project="test-project")
        bq.client = mock_bigquery_client
        
        with caplog.at_level(logging.INFO):
            bq.batch_load_from_memory(
                data=[],
                dataset="test_dataset",
                table="test_table"
            )
        
        # Verifica que foi chamado mesmo com dados vazios
        mock_bigquery_client.load_table_from_file.assert_called_once()
        
        # Verifica que o arquivo está vazio (apenas uma linha em branco)
        call_args = mock_bigquery_client.load_table_from_file.call_args
        memory_file = call_args[0][0]
        memory_file.seek(0)
        content = memory_file.read().decode('utf-8')
        assert content == ""
    
    # def test_batch_load_json_serialization_error(self, mock_bigquery_client):
    #     """Testa erro na serialização JSON"""
    #     # Dados com objeto não serializável
    #     invalid_data = [
    #         {"id": 1, "obj": object()}  # object() não é JSON serializável
    #     ]
        
    #     bq = BigQuery(project="test-project")
    #     bq.client = mock_bigquery_client
        
    #     with pytest.raises(Exception) as exc_info:
    #         bq.batch_load_from_memory(
    #             data=invalid_data,
    #             dataset="test_dataset",
    #             table="test_table"
    #         )
        
    #     assert "Error converting data to NDJSON" in str(exc_info.value)
    #     mock_bigquery_client.load_table_from_file.assert_not_called()
    
    def test_batch_load_bigquery_error(self, mock_bigquery_client, sample_data, caplog):
        """Testa erro durante o carregamento no BigQuery"""
        mock_load_job = Mock()
        mock_load_job.result.side_effect = GoogleCloudError("BigQuery error")
        
        mock_bigquery_client.load_table_from_file.return_value = mock_load_job
        
        bq = BigQuery(project="test-project")
        bq.client = mock_bigquery_client
        
        with pytest.raises(Exception) as exc_info, caplog.at_level(logging.ERROR):
            bq.batch_load_from_memory(
                data=sample_data,
                dataset="test_dataset",
                table="test_table"
            )
        
        assert "Failed to load data from memory" in caplog.text
        assert "BigQuery error" in str(exc_info.value)
    
    def test_batch_load_with_special_characters(self, mock_bigquery_client, caplog):
        """Testa carregamento com caracteres especiais"""
        test_data = [
            {"id": 1, "text": "Café com açúcar"},
            {"id": 2, "text": "São Paulo - SP"},
            {"id": 3, "text": "Rua Antônio João, 123"}
        ]
        
        mock_load_job = Mock()
        mock_load_job.output_rows = len(test_data)
        mock_load_job.result = Mock()
        
        mock_bigquery_client.load_table_from_file.return_value = mock_load_job
        
        bq = BigQuery(project="test-project")
        bq.client = mock_bigquery_client
        
        bq.batch_load_from_memory(
            data=test_data,
            dataset="test_dataset",
            table="test_table"
        )
        
        # Verifica serialização UTF-8
        call_args = mock_bigquery_client.load_table_from_file.call_args
        memory_file = call_args[0][0]
        memory_file.seek(0)
        content = memory_file.read().decode('utf-8')
        
        for item in test_data:
            assert json.dumps(item) in content
    
    # @patch('modules.cloud_function.cf_delivery_sensor.src.utils.bigquery.io.BytesIO')
    # def test_memory_file_cleanup_on_error(self, mock_bytesio, mock_bigquery_client, sample_data):
    #     """Testa que o arquivo em memória é fechado em caso de erro"""
    #     mock_file = Mock()
    #     mock_file.write = Mock()
    #     mock_file.seek = Mock()
    #     mock_file.close = Mock()
        
    #     mock_bytesio.return_value = mock_file
        
    #     # Simula erro na escrita
    #     mock_file.write.side_effect = Exception("Write error")
        
    #     bq = BigQuery(project="test-project")
    #     bq.client = mock_bigquery_client
        
    #     with pytest.raises(Exception):
    #         bq.batch_load_from_memory(
    #             data=sample_data,
    #             dataset="test_dataset",
    #             table="test_table"
    #         )
        
    #     # O arquivo deve ter sido fechado mesmo com erro
    #     mock_file.close.assert_called()


# class TestGetQuery:
#     """Testes para o método get_query"""
    
#     @patch('utils.bigquery.bigquery.Client')
#     def test_get_purchase_query(self, mock_client):
#         """Testa obtenção da query de compras"""
#         project_id = "test-project"
#         bq = BigQuery(project=project_id)
        
#         query = bq.get_query("purchase_query")
        
#         assert isinstance(query, str)
#         assert "purchase_id" in query
#         assert "tb_sales" in query
#         assert "tb_inventory" in query
#         assert "tb_customers" in query
#         assert "tb_address" in query
#         assert project_id in query
#         assert "RAND()" in query
#         assert "LIMIT 10000" in query
    
#     @patch('utils.bigquery.bigquery.Client')
#     def test_get_delivery_query(self, mock_client):
#         """Testa obtenção da query de entrega"""
#         project_id = "test-project"
#         bq = BigQuery(project=project_id)
        
#         query = bq.get_query("delivery_query")
        
#         assert isinstance(query, str)
#         assert "vehicle_id" in query
#         assert "tb_vehicles" in query
#         assert "tb_inventory" in query
#         assert "average_speed_km_h" in query
#         assert "capacity_kg" in query
#         assert "coordinates.latitude" in query
#         assert project_id in query
#         assert "DISTINCT" in query
#         assert 'status = "available"' in query
    
#     @patch('utils.bigquery.bigquery.Client')
#     def test_get_query_invalid_key(self, mock_client):
#         """Testa tentativa de obter query com chave inválida"""
#         bq = BigQuery(project="test-project")
        
#         with pytest.raises(KeyError) as exc_info:
#             bq.get_query("invalid_query_key")
        
#         assert "invalid_query_key" in str(exc_info.value)
    
#     @patch('utils.bigquery.bigquery.Client')
#     @pytest.mark.parametrize("query_key", ["purchase_query", "delivery_query"])
#     def test_get_query_all_keys(self, mock_client, query_key):
#         """Testa todas as chaves de query disponíveis"""
#         bq = BigQuery(project="test-project")
        
#         # Não deve levantar exceção para chaves válidas
#         query = bq.get_query(query_key)
#         assert isinstance(query, str)
#         assert len(query) > 0


# class TestReadBQ:
#     """Testes para o método read_bq"""
    
#     @pytest.fixture
#     def mock_query_result(self):
#         """Fixture que simula resultado de query"""
#         # Cria rows mockadas
#         mock_rows = []
#         for i in range(3):
#             mock_row = Mock()
#             mock_row.__iter__ = Mock(return_value=iter([f"col1_{i}", f"col2_{i}", i]))
#             mock_rows.append(mock_row)
        
#         mock_result = Mock()
#         mock_result.__iter__ = Mock(return_value=iter(mock_rows))
#         return mock_result
    
#     @patch('utils.bigquery.bigquery.Client')
#     def test_read_bq_success(self, mock_client_class, mock_query_result):
#         """Testa execução bem-sucedida de query"""
#         # Setup
#         mock_client = Mock()
#         mock_query_job = Mock()
#         mock_query_job.result.return_value = mock_query_result
        
#         mock_client.query.return_value = mock_query_job
#         mock_client_class.return_value = mock_client
        
#         # Execute
#         bq = BigQuery(project="test-project")
#         query = "SELECT * FROM test_table"
        
#         result = bq.read_bq(query)
        
#         # Verify
#         mock_client.query.assert_called_once()
        
#         # Verifica configuração da query
#         call_args = mock_client.query.call_args
#         assert call_args[0][0] == query
        
#         job_config = call_args[1]['job_config']
#         assert job_config.use_legacy_sql is False
        
#         # Verifica resultado
#         assert isinstance(result, list)
#         assert len(result) == 3
        
#         for i, row in enumerate(result):
#             assert isinstance(row, list)
#             assert row == [f"col1_{i}", f"col2_{i}", i]
    
#     @patch('utils.bigquery.bigquery.Client')
#     def test_read_bq_empty_result(self, mock_client_class):
#         """Testa query que retorna resultados vazios"""
#         mock_client = Mock()
#         mock_query_job = Mock()
#         mock_query_job.result.return_value = []  # Resultado vazio
        
#         mock_client.query.return_value = mock_query_job
#         mock_client_class.return_value = mock_client
        
#         bq = BigQuery(project="test-project")
#         result = bq.read_bq("SELECT * FROM empty_table")
        
#         assert result == []
    
#     @patch('utils.bigquery.bigquery.Client')
#     def test_read_bq_with_complex_query(self, mock_client_class, mock_query_result):
#         """Testa query com parâmetros complexos"""
#         mock_client = Mock()
#         mock_query_job = Mock()
#         mock_query_job.result.return_value = mock_query_result
        
#         mock_client.query.return_value = mock_query_job
#         mock_client_class.return_value = mock_client
        
#         bq = BigQuery(project="test-project")
        
#         complex_query = """
#             SELECT 
#                 user_id,
#                 COUNT(*) as transaction_count,
#                 SUM(amount) as total_amount
#             FROM transactions
#             WHERE date >= '2024-01-01'
#             GROUP BY user_id
#             HAVING total_amount > 1000
#             ORDER BY total_amount DESC
#         """
        
#         result = bq.read_bq(complex_query)
        
#         # mock_client.query.assert_called_once_with(complex_query, job_config=mock.ANY)
    
#     @patch('utils.bigquery.bigquery.Client')
#     def test_read_bq_query_error(self, mock_client_class):
#         """Testa erro na execução da query"""
#         mock_client = Mock()
#         mock_client.query.side_effect = GoogleCloudError("Query execution failed")
        
#         mock_client_class.return_value = mock_client
        
#         bq = BigQuery(project="test-project")
        
#         with pytest.raises(GoogleCloudError) as exc_info:
#             bq.read_bq("SELECT * FROM non_existent_table")
        
#         assert "Query execution failed" in str(exc_info.value)
    
#     @patch('utils.bigquery.bigquery.Client')
#     def test_read_bq_with_get_query_integration(self, mock_client_class, mock_query_result):
#         """Testa integração entre get_query e read_bq"""
#         mock_client = Mock()
#         mock_query_job = Mock()
#         mock_query_job.result.return_value = mock_query_result
        
#         mock_client.query.return_value = mock_query_job
#         mock_client_class.return_value = mock_client
        
#         bq = BigQuery(project="test-project")
        
#         # Obtém a query usando get_query
#         query = bq.get_query("purchase_query")
        
#         # Executa a query usando read_bq
#         result = bq.read_bq(query)
        
#         # Verificações
#         mock_client.query.assert_called_once()
#         assert "purchase_id" in query  # Garante que é a query correta
#         assert len(result) == 3


# class TestIntegrationScenarios:
#     """Cenários de integração que testam múltiplos métodos juntos"""
    
#     @patch('utils.bigquery.bigquery.Client')
#     def test_full_flow_purchase_data(self, mock_client_class):
#         """Testa fluxo completo: gerar dados, carregar, consultar"""
#         # Setup mocks
#         mock_client = Mock()
        
#         # Mock para batch_load
#         mock_load_job = Mock()
#         mock_load_job.output_rows = 5
#         mock_load_job.result = Mock()
        
#         # Mock para read_bq
#         mock_query_job = Mock()
#         mock_query_result = Mock()
#         mock_rows = [Mock(), Mock()]
#         for i, row in enumerate(mock_rows):
#             row.__iter__ = Mock(return_value=iter([i, f"customer_{i}", f"address_{i}"]))
#         mock_query_result.__iter__ = Mock(return_value=iter(mock_rows))
#         mock_query_job.result.return_value = mock_query_result
        
#         mock_client.load_table_from_file.return_value = mock_load_job
#         mock_client.query.return_value = mock_query_job
        
#         mock_client_class.return_value = mock_client
        
#         # Execute
#         bq = BigQuery(project="integration-test")
        
#         # 1. Carrega dados
#         sample_data = [
#             {"purchase_id": i, "product": f"Product {i}", "amount": i * 10}
#             for i in range(5)
#         ]
        
#         bq.batch_load_from_memory(
#             data=sample_data,
#             dataset="sales",
#             table="purchases"
#         )
        
#         # 2. Consulta dados
#         query = bq.get_query("purchase_query")
#         result = bq.read_bq(query)
        
#         # Verify
#         mock_client.load_table_from_file.assert_called_once()
#         mock_client.query.assert_called_once()
#         assert len(result) == 2
    
#     @patch('utils.bigquery.bigquery.Client')
#     def test_error_recovery_flow(self, mock_client_class, caplog):
#         """Testa fluxo com erro e recuperação"""
#         mock_client = Mock()
        
#         # Primeira chamada falha, segunda sucede
#         mock_load_job = Mock()
#         mock_load_job.result.side_effect = [
#             GoogleCloudError("Temporary error"),
#             None  # Segunda chamada bem-sucedida
#         ]
#         mock_load_job.output_rows = 3
        
#         mock_client.load_table_from_file.return_value = mock_load_job
        
#         mock_client_class.return_value = mock_client
        
#         bq = BigQuery(project="recovery-test")
#         bq.client = mock_client
        
#         sample_data = [{"id": i} for i in range(3)]
        
#         # Primeira tentativa deve falhar
#         with pytest.raises(GoogleCloudError):
#             bq.batch_load_from_memory(
#                 data=sample_data,
#                 dataset="test",
#                 table="table"
#             )
        
#         # Segunda tentativa deve funcionar
#         # (Em um cenário real, você teria lógica de retry)
#         mock_load_job.result.side_effect = None  # Remove o erro
#         mock_load_job.result.return_value = None
        
#         bq.batch_load_from_memory(
#             data=sample_data,
#             dataset="test",
#             table="table"
#         )
        
#         assert mock_client.load_table_from_file.call_count == 2


# class TestBigQueryPerformance:
#     """Testes de performance (simulados)"""
    
#     @patch('utils.bigquery.bigquery.Client')
#     def test_batch_load_large_dataset(self, mock_client_class):
#         """Testa carregamento de grande volume de dados"""
#         mock_client = Mock()
#         mock_load_job = Mock()
#         mock_load_job.output_rows = 10000
#         mock_load_job.result = Mock()
        
#         mock_client.load_table_from_file.return_value = mock_load_job
#         mock_client_class.return_value = mock_client
        
#         bq = BigQuery(project="perf-test")
        
#         # Gera grande volume de dados
#         large_data = [
#             {"id": i, "data": "x" * 100, "value": i * 1.5}
#             for i in range(10000)
#         ]
        
#         # Isso deve funcionar sem problemas de memória
#         bq.batch_load_from_memory(
#             data=large_data,
#             dataset="large",
#             table="dataset"
#         )
        
#         # Verifica que todos os dados foram escritos
#         call_args = mock_client.load_table_from_file.call_args
#         memory_file = call_args[0][0]
#         memory_file.seek(0)
#         lines = memory_file.read().decode('utf-8').strip().split('\n')
        
#         assert len(lines) == 10000
    
#     @patch('utils.bigquery.bigquery.Client')
#     @patch('utils.bigquery.time')
#     def test_query_performance_monitoring(self, mock_time, mock_client_class):
#         """Testa monitoramento de performance de queries"""
#         mock_client = Mock()
#         mock_query_job = Mock()
        
#         # Simula tempo de execução
#         mock_time.time.side_effect = [100.0, 102.5]  # 2.5 segundos
        
#         mock_query_result = Mock()
#         mock_query_result.__iter__ = Mock(return_value=iter([]))
#         mock_query_job.result.return_value = mock_query_result
        
#         mock_client.query.return_value = mock_query_job
#         mock_client_class.return_value = mock_client
        
#         bq = BigQuery(project="perf-test")
        
#         # Em produção, você pode adicionar logging de tempo
#         import logging
#         logging.basicConfig(level=logging.INFO)
        
#         with patch.object(logging.getLogger(), 'info') as mock_log:
#             result = bq.read_bq("SELECT * FROM large_table")
            
#             # Verifica se log de performance foi feito
#             # (adicione essa lógica na sua classe se necessário)
#             assert result == []


# # Testes adicionais para edge cases
# class TestBigQueryEdgeCases:
#     """Testes para casos de borda"""
    
#     @patch('utils.bigquery.bigquery.Client')
#     def test_project_id_with_special_chars(self, mock_client_class):
#         """Testa project ID com caracteres especiais"""
#         mock_client = Mock()
#         mock_client_class.return_value = mock_client
        
#         special_project = "project-123_abc.DEF"
#         bq = BigQuery(project=special_project)
        
#         assert bq.project == special_project
#         mock_client_class.assert_called_once_with(special_project)
    
#     @patch('utils.bigquery.bigquery.Client')
#     def test_dataset_table_names_with_dashes(self, mock_client_class):
#         """Testa dataset e table names com hífens"""
#         mock_client = Mock()
#         mock_load_job = Mock()
#         mock_load_job.output_rows = 1
#         mock_load_job.result = Mock()
        
#         mock_client.load_table_from_file.return_value = mock_load_job
#         mock_client_class.return_value = mock_client
        
#         bq = BigQuery(project="test-project")
        
#         bq.batch_load_from_memory(
#             data=[{"id": 1}],
#             dataset="my-dataset",
#             table="my-table"
#         )
        
#         # Verifica que o table_id foi construído corretamente
#         call_args = mock_client.load_table_from_file.call_args
#         table_id = call_args[0][1]
#         assert table_id == "test-project.my-dataset.my-table"
    
#     @patch('utils.bigquery.bigquery.Client')
#     def test_none_values_in_data(self, mock_client_class):
#         """Testa dados com valores None/Null"""
#         mock_client = Mock()
#         mock_load_job = Mock()
#         mock_load_job.output_rows = 2
#         mock_load_job.result = Mock()
        
#         mock_client.load_table_from_file.return_value = mock_load_job
#         mock_client_class.return_value = mock_client
        
#         bq = BigQuery(project="test-project")
        
#         data_with_none = [
#             {"id": 1, "name": "Test", "optional_field": None},
#             {"id": 2, "name": None, "optional_field": "Value"}
#         ]
        
#         bq.batch_load_from_memory(
#             data=data_with_none,
#             dataset="test",
#             table="table"
#         )
        
#         # Verifica serialização de None para null JSON
#         call_args = mock_client.load_table_from_file.call_args
#         memory_file = call_args[0][0]
#         memory_file.seek(0)
#         content = memory_file.read().decode('utf-8')
        
#         assert '"optional_field": null' in content
#         assert '"name": null' in content


# # Para executar os testes com cobertura
# if __name__ == "__main__":
#     pytest.main([__file__, "-v", "--tb=short", "--cov=utils.bigquery", "--cov-report=term-missing"])