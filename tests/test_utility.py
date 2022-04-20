from Taipower.utility import des_decrypt, des_encrypt, get_random_key

class TestUtility:
    def test_get_random_key(self):
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_abcdefghijklmnopqrstuvwxyz"
        key = get_random_key(16)
        assert len(key) == 16
        for char in key:
            assert char in chars
    
    def test_des_encrypt_decrypt(self):
        mock_plain_text = "Taipower"
        
        encrypted_text = des_encrypt(mock_plain_text)
        assert encrypted_text[32] == "@"
        plain_text = des_decrypt(encrypted_text)
        assert mock_plain_text == plain_text
