import os
import unittest
import json

from werkzeug.datastructures import FileStorage

from tests.BaseCase import BaseCase

TEST_FILES_PATH = os.path.join('tests', 'test-files')
TEST_FILENAME = 'pix Kaity Khatkeen.jpeg'
TEST_PIX_IMAGE = os.path.join(TEST_FILES_PATH, TEST_FILENAME)


class TestWhatsappPix(BaseCase):

    def test_read_whatsapp_pix(self):

        mock_file = FileStorage(
            stream=open(TEST_PIX_IMAGE, 'rb'),
            filename=TEST_FILENAME,
            content_type="image/jpeg",
        )

        response = self.app.post(
            '/read-whatsapp-pix',
            data={
                'pix': mock_file,
            },
            follow_redirects=True,
            content_type='multipart/form-data',
        )

        pix_infos = response.json['pix_infos']
        self.assertEqual(len(pix_infos), 1)

        mock_info = pix_infos[0]
        self.assertEqual(mock_info['fileName'], TEST_FILENAME)
        self.assertEqual(mock_info['value'], 'R$ 88,59')
        self.assertEqual(mock_info['name'], 'Kaity Khatkeen')
        self.assertEqual(mock_info['pix_key'], '77998022502')
