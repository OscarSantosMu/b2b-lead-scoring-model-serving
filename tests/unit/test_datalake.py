import os
import unittest
from unittest.mock import MagicMock, patch

import api.app.datalake as datalake_module
from api.app.datalake import (
    AzureDataLakeWriter,
    NoOpDataLakeWriter,
    S3DataLakeWriter,
    get_datalake_writer,
    write_scoring_result,
)


class TestDataLake(unittest.TestCase):
    def setUp(self):
        # Reset the global writer instance before each test
        datalake_module._writer_instance = None

    def tearDown(self):
        # Reset the global writer instance after each test
        datalake_module._writer_instance = None

    def test_noop_writer(self):
        writer = NoOpDataLakeWriter()
        result = writer.write_result(
            lead_id="test_lead",
            bucket=1,
            tier="High",
            raw_score=0.95,
            model_version="v1",
            timestamp="2023-01-01T00:00:00Z",
            features={},
        )
        self.assertTrue(result)

        batch_result = writer.write_batch_results([{}])
        self.assertTrue(batch_result)

    @patch.dict(os.environ, {"DATALAKE_PROVIDER": "none"})
    def test_get_datalake_writer_none(self):
        writer = get_datalake_writer()
        self.assertIsInstance(writer, NoOpDataLakeWriter)

    @patch.dict(os.environ, {"DATALAKE_PROVIDER": "s3"})
    def test_get_datalake_writer_s3(self):
        writer = get_datalake_writer()
        self.assertIsInstance(writer, S3DataLakeWriter)

    @patch.dict(os.environ, {"DATALAKE_PROVIDER": "azure"})
    def test_get_datalake_writer_azure(self):
        writer = get_datalake_writer()
        self.assertIsInstance(writer, AzureDataLakeWriter)

    @patch.dict(os.environ, {"DATALAKE_PROVIDER": "unknown"})
    def test_get_datalake_writer_default(self):
        writer = get_datalake_writer()
        self.assertIsInstance(writer, NoOpDataLakeWriter)

    @patch("api.app.datalake.get_datalake_writer")
    def test_write_scoring_result_success(self, mock_get_writer):
        mock_writer = MagicMock()
        mock_writer.write_result.return_value = True
        mock_get_writer.return_value = mock_writer

        result = write_scoring_result(
            lead_id="test_lead",
            bucket=1,
            tier="High",
            raw_score=0.95,
            model_version="v1",
            timestamp="2023-01-01T00:00:00Z",
            features={},
        )

        self.assertTrue(result)
        mock_writer.write_result.assert_called_once_with(
            lead_id="test_lead",
            bucket=1,
            tier="High",
            raw_score=0.95,
            model_version="v1",
            timestamp="2023-01-01T00:00:00Z",
            features={},
        )

    @patch("api.app.datalake.get_datalake_writer")
    def test_write_scoring_result_exception(self, mock_get_writer):
        mock_writer = MagicMock()
        mock_writer.write_result.side_effect = Exception("Test error")
        mock_get_writer.return_value = mock_writer

        result = write_scoring_result(
            lead_id="test_lead",
            bucket=1,
            tier="High",
            raw_score=0.95,
            model_version="v1",
            timestamp="2023-01-01T00:00:00Z",
            features={},
        )

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
