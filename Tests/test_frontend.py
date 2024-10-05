import unittest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock
from io import StringIO
from frontend.cli import CLI
from frontend.config import Config

class TestGGUFMetadataModifierFrontend(unittest.TestCase):

    def setUp(self):
        self.config = Config(debug=True)
        self.cli = CLI(self.config)
        self.temp_dir = tempfile.mkdtemp()
        self.gguf_file = os.path.join(self.temp_dir, "test.gguf")
        self.json_file = os.path.join(self.temp_dir, "test.json")

        # Create a mock GGUF file
        with open(self.gguf_file, "w") as f:
            f.write("MOCK GGUF FILE")

    def tearDown(self):
        # Clean up temporary files
        os.remove(self.gguf_file)
        if os.path.exists(self.json_file):
            os.remove(self.json_file)
        os.rmdir(self.temp_dir)

    @patch('frontend.cli.subprocess.run')
    def test_modify_metadata(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        result = self.cli.modify_metadata(self.gguf_file, "test_key", "test_value", "string")
        self.assertTrue(result)
        mock_run.assert_called_once_with(
            ["gguf_metadata_modifier", "modify", self.gguf_file, "test_key", "test_value", "string"],
            capture_output=True, text=True
        )

    @patch('frontend.cli.subprocess.run')
    def test_remove_metadata(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        result = self.cli.remove_metadata(self.gguf_file, "test_key")
        self.assertTrue(result)
        mock_run.assert_called_once_with(
            ["gguf_metadata_modifier", "remove", self.gguf_file, "test_key"],
            capture_output=True, text=True
        )

    @patch('frontend.cli.subprocess.run')
    def test_export_metadata(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        result = self.cli.export_metadata(self.gguf_file, self.json_file)
        self.assertTrue(result)
        mock_run.assert_called_once_with(
            ["gguf_metadata_modifier", "export", self.gguf_file, self.json_file],
            capture_output=True, text=True
        )

    @patch('frontend.cli.subprocess.run')
    def test_import_metadata(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        result = self.cli.import_metadata(self.gguf_file, self.json_file)
        self.assertTrue(result)
        mock_run.assert_called_once_with(
            ["gguf_metadata_modifier", "import", self.gguf_file, self.json_file],
            capture_output=True, text=True
        )

    @patch('frontend.cli.subprocess.run')
    def test_search_metadata(self, mock_run):
        mock_output = json.dumps([
            {"key": "test_key1", "value": "test_value1", "type": "string"},
            {"key": "test_key2", "value": 42, "type": "int"}
        ])
        mock_run.return_value = MagicMock(returncode=0, stdout=mock_output)
        result = self.cli.search_metadata(self.gguf_file, "test")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["key"], "test_key1")
        self.assertEqual(result[1]["value"], 42)
        mock_run.assert_called_once_with(
            ["gguf_metadata_modifier", "search", self.gguf_file, "test"],
            capture_output=True, text=True
        )

    @patch('sys.stdout', new_callable=StringIO)
    @patch('frontend.cli.subprocess.run')
    def test_process_file_with_config(self, mock_run, mock_stdout):
        mock_run.return_value = MagicMock(returncode=0)
        user_config = {
            "metadata_to_modify": [
                {"key": "model_name", "value": "Test Model", "type": "string"}
            ],
            "metadata_to_add": [
                {"key": "custom_param", "value": 0.5, "type": "float"}
            ],
            "metadata_to_remove": ["unused_param"]
        }
        self.cli.process_file_with_config(self.gguf_file, user_config)
        
        self.assertEqual(mock_run.call_count, 3)
        modify_call, add_call, remove_call = mock_run.call_args_list
        
        self.assertEqual(modify_call[0][0], ["gguf_metadata_modifier", "modify", self.gguf_file, "model_name", "Test Model", "string"])
        self.assertEqual(add_call[0][0], ["gguf_metadata_modifier", "modify", self.gguf_file, "custom_param", "0.5", "float"])
        self.assertEqual(remove_call[0][0], ["gguf_metadata_modifier", "remove", self.gguf_file, "unused_param"])
        
        self.assertIn("Processing complete", mock_stdout.getvalue())

    @patch('frontend.cli.subprocess.run')
    def test_error_handling(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stderr="Error message")
        with self.assertRaises(RuntimeError):
            self.cli.modify_metadata(self.gguf_file, "test_key", "test_value", "string")

    @patch('frontend.config.json.dump')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_save_config(self, mock_open, mock_json_dump):
        self.config.save_config({"test_key": "test_value"})
        mock_open.assert_called_once_with(self.config.config_path, 'w')
        mock_json_dump.assert_called_once()

    @patch('frontend.config.json.load')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_load_config(self, mock_open, mock_json_load):
        mock_json_load.return_value = {"test_key": "test_value"}
        result = self.config.load_config()
        self.assertEqual(result, {"test_key": "test_value"})
        mock_open.assert_called_once_with(self.config.config_path, 'r')

if __name__ == '__main__':
    unittest.main()
