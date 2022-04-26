from Taipower.utility import des_decrypt, des_encrypt, get_random_key, roc_year_to_wastern

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
    
    def test_roc_year_to_wastern(self):
        mock_roc_date = "111/03/05"
        assert roc_year_to_wastern(mock_roc_date) == "2022/03/05"
        mock_roc_date = "1100406"
        assert roc_year_to_wastern(mock_roc_date) == "20210406"
