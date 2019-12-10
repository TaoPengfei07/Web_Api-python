import requests
import json
import unittest
import re
import time

RPC_URL = 'http://127.0.0.1:6765'
WEBAPI_URL = 'http://39.105.101.31:50615/apis'

def is_account(str):
    if re.findall(r'czr_[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{50,}$', str):
        return True
    else:
        return False

# judge gas
def is_gas(str):
    return is_number(str)

# judge number
def is_number(str):
    if str.isdigit():
        return True
    else:
        return False

# judge hex
def is_hex(str, is_lens=None):
    if is_lens is None:
        if re.findall(r"^[A-F0-9]*$", str) and len(str) % 2 == 0:
            return True
        else:
            return False
    else:
        if re.findall(r"^[A-F0-9]{{{0}}}$".format(is_lens), str):
            return True
        else:
            return False

# judge hex
def hex_is(str,is_lens=None):
    if is_lens is None:
        if re.findall(r'^[a-fA-F0-9]*$',str) and len(str) % 2 == 0:
            return True
        else:
            return False

# judge signature
def is_signature(str):
    if is_hex(str, 128):
        return True
    else:
        return False

# judge bool
def is_bool(str):
    if isinstance(str, bool):
        return True
    else:
        return False

# judge int
def is_int(str):
    if isinstance(str, int):
        return True
    else:
        return False

# judge str
def is_str(i):
    if isinstance(i, str):
        return True
    else:
        return False

# judge version
def is_version(i):
    if re.findall("\d+\.\d+\.\d+", i):
        return True
    else:
        return False

# judge json
def try_load_json(jsonstr):
    try:
        json_data = json.loads(jsonstr)
        return True, json_data
    except ValueError as e:
        return False, None

class Test_webapi(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        data = {
                "action": "account_create",
                "password": "12345678"
                }
        response = requests.post(url=RPC_URL,data=json.dumps(data))
        json_data = json.loads(response.text)
        globals()["new_account"] = json_data['account']
        globals()["pka_account"] = "czr_37nQ9qXcfUewfr9uaP5cnb5c9F465sUh1YVuZWhVz6SBJN84kE"
        globals()["contract_account"] = "czr_4FWGvTq15awoaXLx7DPb2zigE7wW8NRDmuJUAyU7YPDADDPb7e"

    '''
    {
    "action": "account_import",
    "json": "{\"account\":\"czr_3dUnMEsuSiUsKGgfft5VDpM2bX9S6T4ppApHRfn1cBmn2znyEv\",\"kdf_salt\":\"175DCAF994E6992AAD1369014670C086\",\"iv\":\"F6054D9B144A254D3D4EAB78C95F21B6\",\"ciphertext\":\"2A943F3A7316C33B16374D9076FEF5BA7770C2A0424A08501D3663A1467DEDD7\"}"
    }
    '''
    def test_import_account(self):
        data = {
            "action": "account_import",
            "json": "{\"account\":\"czr_33EuccjKjcZgwbHYp8eLhoFiaKGARVigZojeHzySD9fQ1ysd7u\",\"kdf_salt\":\"774DDE2B6D01D6A2B000BB42F8118E2C\",\"iv\":\"5EF469016DB117B4437FB46D37BFA925\",\"ciphertext\":\"2B9567F4184B4D0A4AD9D5A3BF94805662B562167AFBEC575B06C23F708F0CA0\"}"
            }
        response = requests.post(url=RPC_URL,data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        is_json, json_data = try_load_json(response.text)
        self.assertTrue(is_json, response.text)
        self.assertEqual(json_data['code'], 0, json_data['msg'])
        self.assertEqual(json_data['msg'], 'OK', json_data['code'])
        json_account = json_data['account']
        self.assertTrue(is_account(json_account), json_account)

    '''
    {
    "action": "send_block",
    "from": "czr_33EuccjKjcZgwbHYp8eLhoFiaKGARVigZojeHzySD9fQ1ysd7u",
    "to": "czr_3dUnMEsuSiUsKGgfft5VDpM2bX9S6T4ppApHRfn1cBmn2znyEv",
    "amount": "1000000000000000000",//1个CZR
    "password": "12345678",
    "gas": "21000",
    "gas_price": "1000000000",
    "data": ""
    }
    '''
    def test_send_block(self):
        data = {
            "action": "send_block",
            "from": "czr_33EuccjKjcZgwbHYp8eLhoFiaKGARVigZojeHzySD9fQ1ysd7u",
            "to": globals()["new_account"],
            "amount": "100000000000000000000",
            "password": "12345678",
            "gas": "60000",
            "gas_price": "100000000000",
            "data": ""
        }
        response = requests.post(url=RPC_URL, data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        is_json, json_data = try_load_json(response.text)
        self.assertTrue(is_json, response.text)
        json_data = json.loads(response.text)
        json_hash = json_data['hash']
        self.assertEqual(json_data['code'], 0, json_data['msg'])
        while True:
            time.sleep(1)
            data1 = {
                "module": "transaction",
                "action": "tx_details",
                "hash": json_hash,
                "apikey": "YourApiKeyToken"
            }
            response = requests.get(url=WEBAPI_URL, params = data1)
            self.assertEqual(response.status_code, 200)
            is_json, json_data = try_load_json(response.text)
            self.assertTrue(is_json, response.text)
            json_data = json.loads(response.text)
            self.assertEqual(json_data['code'], 100, json_data['msg'])
            json_datas = json_data['result']
            if len(json_datas) == 0:
                continue
            if json_datas[0]['status'] == '0':
                break

        data2 = {
                "module": "transaction",
                "action": "tx_offline_generation",
                "from": "czr_33EuccjKjcZgwbHYp8eLhoFiaKGARVigZojeHzySD9fQ1ysd7u",
                "to": globals()["new_account"],
                "amount": "1000000000000000000",
                "gas": "60000",
                "gas_price": "1000000000000",
                "previous": json_hash,
                "data": "",
                "apikey": "YourApiKeyToken"
            }
        response = requests.get(url=WEBAPI_URL, params=data2)
        self.assertEqual(response.status_code, 200)
        is_json, json_data = try_load_json(response.text)
        self.assertTrue(is_json, response.text)
        json_data = json.loads(response.text)
        self.assertEqual(json_data['code'], 100, json_data['msg'])
        json_datas = json_data['result']
        json_previous = json_datas['previous']
        self.assertTrue(len(json_datas) > 0, json_datas)
        self.assertTrue(is_hex(json_datas['hash']), json_datas)
        self.assertTrue(is_account(json_datas['from']), json_datas)
        self.assertTrue(is_account(json_datas['to']), json_datas)
        self.assertTrue(is_number(json_datas['amount']), json_datas)
        self.assertTrue(is_number(json_datas['gas']), json_datas)
        self.assertTrue(is_number(json_datas['gas_price']), json_datas)
        self.assertTrue(is_hex(json_datas['previous']), json_datas)
        self.assertTrue(is_str(json_datas['data']), json_datas)

        data3 = {
            "action": "sign_msg",
            "public_key": data2["from"],
            "password": "12345678",
            "msg": json_datas['hash']
        }
        response = requests.post(url=RPC_URL, data=json.dumps(data3))
        self.assertEqual(response.status_code, 200)
        is_json, json_data = try_load_json(response.text)
        self.assertTrue(is_json, response.text)
        json_data = json.loads(response.text)
        self.assertEqual(json_data['code'], 0, json_data['msg'])
        json_sign = json_data['signature']
        self.assertTrue(is_signature(json_sign), json_sign)

        data4 = {
            "module": "transaction",
            "action": "tx_offline_sending",
            "from": json_datas['from'],
            "to": json_datas['to'],
            "amount": json_datas['amount'],
            "gas": json_datas['gas'],
            "gas_price": json_datas['gas_price'],
            "data": "",
            "signature": json_sign,
            "previous": json_previous,
            "gen_next_work": "1",
            "apikey": "YourApiKeyToken"
        }
        response = requests.get(url=WEBAPI_URL, params=data4)
        self.assertEqual(response.status_code, 200)
        is_json, json_data = try_load_json(response.text)
        self.assertTrue(is_json, response.text)
        json_data = json.loads(response.text)
        self.assertEqual(json_data['code'], 100, json_data['msg'])
        json_datas = json_data['result']
        self.assertTrue(is_hex(json_datas), json_datas)


    '''
    module  : account
    action  : account_validate
    account : czr_xxxxxxx 
    apikey  : YouApikey
    '''
    def test_validate_account(self):
        data = {
            "module": "account",
            "action": "account_validate",
            "account": globals()["new_account"],
            "apikey": "YourApiKeyToken"
        }
        response = requests.get(url=WEBAPI_URL,params=data)
        self.assertEqual(response.status_code, 200)
        is_json, json_data = try_load_json(response.text)
        self.assertTrue(is_json, response.text)
        json_data = json.loads(response.text)
        self.assertEqual(json_data['code'], 100, json_data['msg'])
        self.assertTrue(is_bool(json_data['result']), json_data['result'])


    '''
    module  : account
    action  : account_balance
    account : czr_account
    apikey  : YourApiKeyToken
    '''
    def test_account_balance(self):
        data = {
            "module": "account",
            "action": "account_balance",
            "account": globals()["new_account"],
            "apikey": "YourApiKeyToken"
        }
        response = requests.get(url=WEBAPI_URL,params=data)
        self.assertEqual(response.status_code, 200)
        is_json, json_data = try_load_json(response.text)
        self.assertTrue(is_json, response.text)
        json_data = json.loads(response.text)
        self.assertEqual(json_data['code'], 100, json_data['msg'])
        json_balance = json_data['result']
        self.assertTrue(is_number(json_balance), json_balance)

    '''
    module  : account
    action  : account_balance_multi
    account : czr_account1,czr_account2
    apikey  : YourApiKeyToken
    '''
    def test_account_balance_multi(self):
        data = {
            "module": "account",
            "action": "account_balance_multi",
            "account": globals()["new_account"],
            "apikey": "YourApiKeyToken"
        }
        response = requests.get(url=WEBAPI_URL, params=data)
        self.assertEqual(response.status_code, 200)
        is_json, json_data = try_load_json(response.text)
        self.assertTrue(is_json, response.text)
        json_data = json.loads(response.text)
        self.assertEqual(json_data['code'], 100, json_data['msg'])
        json_datas = json_data['result']
        self.assertTrue(len(json_datas) > 0, json_datas)
        for i in json_datas:
            self.assertTrue(is_number(i['balance']), json_datas)
            self.assertTrue(is_account(i['account']),json_datas)

    '''
    module              : account
    action              : account_balance_token
    account             : czr_xx
    contract_account    : (可选)czr_xx ,指定token账户
    apikey              : YourApiKeyToken
    '''
    def test_account_balance_token(self):
        data = {
            "module": "account",
            "action": "account_balance_token",
            "account": globals()["pka_account"],
            "contract_account": globals()["contract_account"],
            "apikey": "YourApiKeyToken"
        }
        response = requests.get(url=WEBAPI_URL, params=data)
        self.assertEqual(response.status_code, 200)
        is_json, json_data = try_load_json(response.text)
        self.assertTrue(is_json, response.text)
        json_data = json.loads(response.text)
        self.assertEqual(json_data['code'], 100, json_data['msg'])
        json_datas = json_data['result']
        self.assertTrue(len(json_datas) > 0, json_datas)
        self.assertTrue(is_account(json_datas['account']), json_datas)
        self.assertTrue(is_account(json_datas['contract_account']), json_datas)
        self.assertTrue(is_str(json_datas['symbol']), json_datas)
        self.assertTrue(is_number(json_datas['precision']), json_datas)
        self.assertTrue(is_number(json_datas['balance']), json_datas)
        self.assertTrue(is_str(json_datas['?column?']), json_datas)

    '''
    module      : account
    action      : account_txlist
    account     : czr_account
    page        : 1
    limit       : 10
    sort        : desc  // desc | asc
    apikey      : YourApiKeyToken
    '''
    def test_account_txlist(self):
        data = {
            "module": "account",
            "action": "account_txlist",
            "account": 'czr_33EuccjKjcZgwbHYp8eLhoFiaKGARVigZojeHzySD9fQ1ysd7u',
            "page": 1,
            "limit": 10,
            "sort": "desc",
            "apikey": "YourApiKeyToken"
        }
        response = requests.get(url=WEBAPI_URL, params=data)
        self.assertEqual(response.status_code, 200)
        is_json, json_data = try_load_json(response.text)
        self.assertTrue(is_json, response.text)
        json_data = json.loads(response.text)
        self.assertEqual(json_data['code'], 100, json_data['msg'])
        json_datas = json_data['result']
        self.assertTrue(len(json_datas) > 0, json_datas)
        for i in json_datas:
            self.assertTrue(is_hex(i['hash']),json_datas)
            self.assertTrue(is_account(i['from']),json_datas)
            self.assertTrue(is_account(i['to']),json_datas)
            self.assertTrue(is_number(i['amount']),json_datas)
            self.assertTrue(is_number(i['is_stable']),json_datas)
            self.assertTrue(is_number(i['mc_timestamp']), json_datas)
            self.assertTrue(is_number(i['stable_index']), json_datas)
            self.assertTrue(is_number(i['status']), json_datas)
            self.assertTrue(is_number(i['gas']), json_datas)
            self.assertTrue(is_number(i['gas_used']), json_datas)
            self.assertTrue(is_number(i['gas_price']), json_datas)
            self.assertTrue(is_hex(i['previous']), json_datas)
            self.assertTrue(is_str(i['data']), json_datas)

    '''
    module      : account
    action      : account_txlist_internal
    account     : czr_xx
    page        : 1
    limit       : 10
    sort        : desc      // desc | asc
    apikey      : YourApiKeyToken
    '''
    def test_account_txlist_internal(self):
        data = {
            "module": "account",
            "action": "account_txlist_internal",
            "account": globals()["contract_account"],
            "page": 1,
            "limit": 10,
            "sort": "desc",
            "apikey": "YourApiKeyToken"
        }
        response = requests.get(url=WEBAPI_URL, params=data)
        self.assertEqual(response.status_code, 200)
        is_json, json_data = try_load_json(response.text)
        self.assertTrue(is_json, response.text)
        json_data = json.loads(response.text)
        self.assertEqual(json_data['code'], 100, json_data['msg'])
        json_datas = json_data['result']
        self.assertTrue(len(json_datas) > 0, json_datas)
        for i in json_datas:
            self.assertTrue(is_number(i['type']), json_datas)
            self.assertTrue(is_number(i['subtraces']), json_datas)
            json_action = i['action']
            self.assertTrue(is_str(json_action['call_type']), json_action)
            self.assertTrue(is_account(json_action['from']), json_action)
            self.assertTrue(is_account(json_action['to']), json_action)
            self.assertTrue(is_number(json_action['gas']), json_action)
            self.assertTrue(is_hex(json_action['input']), json_action)
            self.assertTrue(is_number(json_action['value']), json_action)
            json_result = i['result']
            self.assertTrue(is_number(json_result['gas_used']), json_action)
            self.assertTrue(is_str(json_result['output']), json_action)
            json_trace_address = i['trace_address']
            for q in json_trace_address:
                self.assertTrue(is_number(q), json_action)

    '''
    module      : account
    action      : account_txlist_count
    account     : czr_xx
    apikey      : YourApiKeyToken
    '''
    def test_account_txlist_count(self):
        data = {
            "module": "account",
            "action": "account_txlist_count",
            "account": 'czr_33EuccjKjcZgwbHYp8eLhoFiaKGARVigZojeHzySD9fQ1ysd7u',
            "apikey": "YourApiKeyToken"
        }
        response = requests.get(url=WEBAPI_URL, params=data)
        self.assertEqual(response.status_code, 200)
        is_json, json_data = try_load_json(response.text)
        self.assertTrue(is_json, response.text)
        json_data = json.loads(response.text)
        self.assertEqual(json_data['code'], 100, json_data['msg'])
        json_datas = json_data['result']
        self.assertTrue(is_number(json_datas), json_datas)

    '''
    module          : account
    action          : account_txlist_token
    account         : czr_xx
    contractaddress : czr_xx
    page            : 1
    limit           : 10
    sort            : desc, // desc | asc
    apikey          : YourApiKeyToken
    '''
    def test_account_txlist_token(self):
        data = {
            "module": "account",
            "action": "account_txlist_token",
            "account": globals()["pka_account"],
            "contractaddress": globals()["contract_account"],
            "page": "1",
            "limit": "10",
            "sort": "desc",
            "apikey": "YourApiKeyToken"
        }
        response = requests.get(url=WEBAPI_URL, params=data)
        self.assertEqual(response.status_code, 200)
        is_json, json_data = try_load_json(response.text)
        self.assertTrue(is_json, response.text)
        json_data = json.loads(response.text)
        self.assertEqual(json_data['code'], 100, json_data['msg'])
        json_datas = json_data['result']
        self.assertTrue(len(json_datas) > 0, json_datas)
        for i in json_datas:
            self.assertTrue(is_number(i['stable_index']), json_datas)
            self.assertTrue(is_hex(i['hash']), json_datas)
            self.assertTrue(is_account(i['from']), json_datas)
            self.assertTrue(is_account(i['to']), json_datas)
            self.assertTrue(is_account(i['contract_account']), json_datas)
            self.assertTrue(is_str(i['token_symbol']), json_datas)
            self.assertTrue(is_number(i['amount']), json_datas)
            self.assertTrue(is_number(i['mc_timestamp']), json_datas)

    '''
    module      : other
    action      : gas_price
    apikey      : YourApiKeyToken
    '''
    def test_gas_price(self):
        data = {
            "module": "other",
            "action": "gas_price",
            "apikey": "YourApiKeyToken"
        }
        response = requests.get(url=WEBAPI_URL, params=data)
        self.assertEqual(response.status_code, 200)
        is_json, json_data = try_load_json(response.text)
        self.assertTrue(is_json, response.text)
        json_data = json.loads(response.text)
        self.assertEqual(json_data['code'], 100, json_data['msg'])
        json_datas = json_data['result']
        self.assertTrue(len(json_datas) > 0, json_datas)
        self.assertTrue(is_number(json_datas['cheapest_gas_price']), json_datas)
        self.assertTrue(is_number(json_datas['median_gas_price']), json_datas)
        self.assertTrue(is_number(json_datas['highest_gas_price']), json_datas)

    '''
    module      : other
    action      : estimate_gas
    apikey      : YourApiKeyToken
    from        :（可选）源账户
    to          :（可选）目标账户
    amount      :（可选）string, 金额，单位：10-18CZR
    gas         :（可选）string, 执行交易使用的gas上限
    gas_price   :（可选）string, gas价格，单位：10-18CZR/gas，手续费 = 实际使用的gas * gas_price
    data        :（可选）智能合约代码或数据。默认为空
    mci         :（可选）string, mci，接受的值："latest", "earliest" 或数字（如:"1352"）, 默认为"latest"
    '''
    def test_estimate_gas(self):
        data = {
            "module": "other",
            "action": "estimate_gas",
            "apikey": "YourApiKeyToken",
            "from": 'czr_33EuccjKjcZgwbHYp8eLhoFiaKGARVigZojeHzySD9fQ1ysd7u',
            "to": globals()["new_account"],
            "amount": "1000000000000000000",
            "gas": "60000",
            "gas_price": "10000000000",
            "data": "",
            "mci": "latest"
        }
        response = requests.get(url=WEBAPI_URL, params=data )
        self.assertEqual(response.status_code, 200)
        is_json, json_data = try_load_json(response.text)
        self.assertTrue(is_json, response.text)
        json_datas = json.loads(response.text)
        self.assertEqual(json_data['code'], 100, json_data['msg'])
        self.assertTrue(is_number(json_datas['result']), json_datas)

    '''
    module      : other
    action      : to_hex
    source      : czr_4KsqkcZCs6i9VU2WUsiqTU8M6i3WYpVPFMcMXSkKmB92GJvYt1
    apikey      : YourApiKeyToken
    '''
    def test_to_hex(self):
        data = {
            "module": "other",
            "action": "to_hex",
            "source": globals()["new_account"],
            "apikey": "YourApiKeyToken"
        }
        response = requests.get(url=WEBAPI_URL, params=data)
        self.assertEqual(response.status_code, 200)
        is_json, json_data = try_load_json(response.text)
        self.assertTrue(is_json, response.text)
        json_data = json.loads(response.text)
        self.assertEqual(json_data['code'], 100, json_data['msg'])
        json_datas = json_data['result']
        self.assertTrue(hex_is(json_datas),json_datas)

if __name__ == "__main__":
    #unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(Test_webapi("test_import_account"))
    suite.addTest(Test_webapi("test_send_block"))
    suite.addTest(Test_webapi("test_validate_account"))
    suite.addTest(Test_webapi("test_account_balance"))
    suite.addTest(Test_webapi("test_account_txlist"))
    suite.addTest(Test_webapi("test_account_balance_multi"))
    suite.addTest(Test_webapi("test_account_balance_token"))
    suite.addTest(Test_webapi("test_account_txlist_internal"))
    suite.addTest(Test_webapi("test_account_txlist_count"))
    suite.addTest(Test_webapi("test_account_txlist_token"))
    suite.addTest(Test_webapi("test_gas_price"))
    suite.addTest(Test_webapi("test_estimate_gas"))
    suite.addTest(Test_webapi("test_to_hex"))
    result = unittest.TextTestRunner(verbosity=3).run(suite)
    if result.wasSuccessful():
        exit(0)
    else:
        exit(1)
