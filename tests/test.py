import unittest
from unittest.mock import patch, MagicMock
import os
import pygame
from gtts import gTTS
from tempfile import NamedTemporaryFile
from my_script import translate_text, speak_caption, capture, query, define, LANGUAGES, API_URL, IMAGE_FILE

class TestProjectZetaFunctions(unittest.TestCase):

    @patch('pygame.camera.Camera')
    def test_capture(self, mock_camera):
        mock_cam_instance = MagicMock()
        mock_camera.return_value = mock_cam_instance
        mock_cam_instance.get_image.return_value = MagicMock()

        # Call capture function
        capture()

        # Assert the camera's start and stop were called
        mock_cam_instance.start.assert_called_once()
        mock_cam_instance.stop.assert_called_once()
        mock_cam_instance.get_image.assert_called_once()

        # Check if image is saved
        self.assertTrue(os.path.exists(IMAGE_FILE))
        
        # Clean up the generated image after test
        os.remove(IMAGE_FILE)

    @patch('requests.post')
    def test_query(self, mock_post):
        # Prepare mock response
        mock_response = MagicMock()
        mock_response.json.return_value = [{"generated_text": "A cat is sitting."}]
        mock_post.return_value = mock_response

        # Call query function
        response = query(IMAGE_FILE)

        # Assert the API call is made correctly
        mock_post.assert_called_once_with(API_URL, headers={'Authorization': 'Bearer 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'}, data=MagicMock())
        
        # Assert the response is handled correctly
        self.assertEqual(response[0]['generated_text'], "A cat is sitting.")

    @patch('gtts.gTTS.save')
    @patch('pygame.mixer.music.play')
    def test_speak_caption(self, mock_play, mock_save):
        # Test text-to-speech function
        caption = "This is a test caption"
        language = LANGUAGES['en']['code']

        speak_caption(caption, language)

        # Assert the speech saving and playing methods are called
        mock_save.assert_called_once()
        mock_play.assert_called_once()

        # Check if the file is removed after play
        temp_filename = mock_save.call_args[0][0]
        self.assertTrue(os.path.exists(temp_filename))
        os.remove(temp_filename)

    @patch('translate.Translator.translate')
    def test_translate_text(self, mock_translate):
        # Mock translation response
        mock_translate.return_value = "This is a translated caption"
        
        translated_text = translate_text("This is a test caption", 'fr')
        self.assertEqual(translated_text, "This is a translated caption")
        
        # Test when the text is already in English
        translated_text = translate_text("This is a test caption", 'en')
        self.assertEqual(translated_text, "This is a test caption")

    @patch('my_script.query')
    @patch('my_script.translate_text')
    @patch('my_script.speak_caption')
    def test_define(self, mock_speak, mock_translate, mock_query):
        # Mock response from query and translation
        mock_query.return_value = [{"generated_text": "A dog is running."}]
        mock_translate.return_value = "A dog is running."

        define()

        # Assert that the query and translation are called
        mock_query.assert_called_once_with(IMAGE_FILE)
        mock_translate.assert_called_once_with("A dog is running.", 'en')

        # Assert that speak_caption is called with translated caption
        mock_speak.assert_called_once_with("A dog is running.", 'en')

    def test_language_dict(self):
        # Assert that the languages are correctly defined
        self.assertTrue('en' in LANGUAGES)
        self.assertTrue('ta' in LANGUAGES)
        self.assertEqual(LANGUAGES['en']['name'], 'English')
        self.assertEqual(LANGUAGES['ta']['name'], 'Tamil')

if __name__ == '__main__':
    unittest.main()
