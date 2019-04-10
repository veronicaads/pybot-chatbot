from rasa_core_sdk import Action
from rasa_core_sdk.events import SlotSet
from rasa_core_sdk.events import UserUtteranceReverted
from rasa_core_sdk.events import AllSlotsReset
from rasa_core_sdk.events import Restarted

import psycopg2
DSN = "postgres://postgres:root@localhost:5432/skripsweet"

import http.client
import jsonpath
import json

class ActionSaveJenisHP(Action):
    def name(self):
        return 'action_save_smartphone_type'
    def run(self, dispatcher, tracker, domain):
        jenishp = next(tracker.get_latest_entity_values("Jenis_HP"), None)
        if not jenishp:
            dispatcher.utter_message("Maaf kak, tolong beritahu kami merk dan tipe smartphone kakak untuk mendapatkan informasi ketersediaan")
            return [UserUtteranceReverted()]
        return [SlotSet('JenisHP',jenishp)]

class ActionCheckStock(Action):
    def name(self):
        return "action_check_stock"

    def run(self, dispatcher, tracker, domain):
        jenishps=tracker.get_slot('JenisHP')
        jenishp = next(tracker.get_latest_entity_values("Jenis_HP"), None)
        if not jenishp:
            dispatcher.utter_message("Maaf kak, tolong beritahu kami merk dan tipe smartphone kakak untuk mendapatkan informasi ketersediaan")
            return [UserUtteranceReverted()]
        if jenishp.lower() in ['xiaomi', 'samsung', 'iphone', 'oppo', 'vivo', 'huawei', 'advan', 'meizu', 'nokia', 'wiko','lg','sony']:
            dispatcher.utter_message("Maaf kak, tolong beritahu kami merk beserta dengan tipe smartphone kakak untuk mendapatkan informasi ketersediaan")
            return [UserUtteranceReverted()]
        with psycopg2.connect(DSN) as conn:
            with conn.cursor() as curs:
                curs.execute(f"""SELECT stock,material_hp,harga,idproduk FROM skripsweet_adminpage_produk WHERE concat(merkhp, ' ', tipehp) LIKE '%{jenishp.lower()}%' """)
                result = curs.fetchall()
                print(result)
                if len(result) == 0:
                    dispatcher.utter_template("utter_reply_ketersediaan_produk_tidak_tersedia",tracker,Jenis_HP=jenishps)
                else:
                    for result_row in result:
                        stock = result_row[0]
                        if int(stock) > 0:
                            dispatcher.utter_template("utter_reply_ketersediaan_produk_tersedia_list",tracker,Material=result_row[1],Harga=result_row[2],IDProduk=result_row[3])           
                        else:
                            dispatcher.utter_template("utter_reply_ketersediaan_produk_tidak_tersedia",tracker,Jenis_HP=jenishp) 
                            return []   
        return []

class ActionSaveMaterial(Action):
    def name(self):
        return 'action_save_material'
    def run(self, dispatcher, tracker, domain):
        material = next(tracker.get_latest_entity_values("Material"), None)
        if not material:
            dispatcher.utter_message("Maaf kak, tolong beritahu kami jenis custom case apa yang kakak inginkan")
            return [UserUtteranceReverted()]
        return [SlotSet('Material',material)]

class ActionReplyLamaPengerjaan(Action):
    def name(self):
        return 'action_reply_lama_pengerjaan'

    def run(self, dispatcher, tracker, domain):
        materials = tracker.get_slot('Material')
        jenishp  = tracker.get_slot('JenisHP')
        material = next(tracker.get_latest_entity_values("Material"), None)
        if not material:
            dispatcher.utter_message("Maaf kak, tolong beritahu kami jenis custom case apa yang kakak inginkan")
            return [UserUtteranceReverted()]
        with psycopg2.connect(DSN) as conn:
            with conn.cursor() as curs:
                curs.execute(f"""SELECT lama_pengerjaan FROM skripsweet_adminpage_produk WHERE concat(merkhp, ' ', tipehp) LIKE 
                '%{jenishp.lower()}%' AND material_hp LIKE '%{materials.lower()}%'  """)
                result = curs.fetchone()
                print(result)
                if result is None:
                    dispatcher.utter_message("Hasil tidak ditemukan. Maaf kak :(")
                    return []   
                else:
                    dispatcher.utter_template("utter_reply_lama_pengerjaan",tracker,Durasi=result[0])   
                    return [] 

class ActionReplyDiTanyaHarga(Action):
    def name(self):
        return 'action_reply_tanya_harga' 
    
    def run(self, dispatcher, tracker, domain):
        materials = tracker.get_slot('Material')
        jenishp  = tracker.get_slot('JenisHP')
        if not jenishp:
            dispatcher.utter_message("Maaf kak, tolong beritahu kami merk dan tipe hp kakak")
            return [UserUtteranceReverted()]
        if not materials:
            dispatcher.utter_message("Maaf kak, tolong beritahu kami jenis custom case apa yang kakak inginkan")
            return [UserUtteranceReverted()]
        with psycopg2.connect(DSN) as conn:
            with conn.cursor() as curs:
                curs.execute(f"""SELECT harga FROM skripsweet_adminpage_produk WHERE concat(merkhp, ' ', tipehp) LIKE '%{jenishp.lower()}%' 
                AND material_hp LIKE '%{materials.lower()}%' AND stock > 0 """)
                result = curs.fetchone()
                if result is None:
                    dispatcher.utter_message("Mohon maaf, material yang kakak tanyakan sedang tidak tersedia.")
                    return []   
                else:
                    dispatcher.utter_template("utter_reply_harga",tracker,JenisHP=jenishp,Material=materials,Harga=result[0])   
                    return [] 
        
class ActionReplyBank(Action):
    def name(self):
        return 'action_reply_bank_tersedia' 
    
    def run(self, dispatcher, tracker, domain):
        namabank = next(tracker.get_latest_entity_values("Nama_Bank"), None)
        dispatcher.utter_message("Bank Pembayaran yang tersedia sesuai keterangan dibawah ini kak :)")
        if not namabank:
            with psycopg2.connect(DSN) as conn:
                with conn.cursor() as curs:
                    curs.execute(f"""SELECT namabank,norek,atasnama FROM skripsweet_adminpage_bank """)
                    result = curs.fetchall()
                    if result is None:
                        dispatcher.utter_message("Kami belum memiliki bank tersebut kak")
                    else:
                        for result_row in result:
                            dispatcher.utter_template("utter_reply_bank_available",tracker,NamaBank=result_row[0],Norek=result_row[1],AtasNama=result_row[2])
                    return []
        else :
             with psycopg2.connect(DSN) as conn:
                with conn.cursor() as curs:
                    curs.execute(f"""SELECT namabank,norek,atasnama FROM skripsweet_adminpage_bank WHERE namabank LIKE '%{namabank.lower()}%' """)
                    result = curs.fetchone()
                    if len(result) == 0:
                        dispatcher.utter_message("Maaf, saat ini kami tidak memiliki rekening bank yang kakak minta")
                    else:
                        print(result)
                        dispatcher.utter_template("utter_reply_bank_available",tracker,NamaBank=result[0],Norek=result[1],AtasNama=result[2])
                    return []

class ActionReplyInfoOlshop(Action):
    def name(self):
        return 'action_reply_lokasi_tersedia' 
    
    def run(self, dispatcher, tracker, domain):
        with psycopg2.connect(DSN) as conn:
            with conn.cursor() as curs:
                curs.execute(f"""SELECT kota_olshop, provinsi_olshop FROM skripsweet_adminpage_info_olshop """)
                result = curs.fetchone()
                dispatcher.utter_template("utter_reply_lokasi_olshop",tracker,Kota=result[0],Provinsi=result[1])
                return []

class ActionReplyInfoLogistik(Action):
    def name(self):
        return 'action_reply_logistik_tersedia' 
    
    def run(self, dispatcher, tracker, domain):
        with psycopg2.connect(DSN) as conn:
            with conn.cursor() as curs:
                curs.execute(f"""SELECT namalogistik FROM skripsweet_adminpage_logistik """)
                result = curs.fetchall()
                if result is not None:
                    dispatcher.utter_message("Saat ini kami menggunakan jasa pengiriman : ")
                    for result_row in result:
                        dispatcher.utter_template("utter_ketersediaan_logistik",tracker,NamaLogistik=result_row[0])
                else:
                    dispatcher.utter_message("Hasil tidak ditemukan ")
        return []

class ActionSaveLokasi(Action):
    def name(self):
        return 'action_save_lokasi'
    def run(self, dispatcher, tracker, domain):
        lokasi = next(tracker.get_latest_entity_values("Lokasi"), None)
        if not lokasi:
            dispatcher.utter_message("Maaf kak, tolong beritahu kami nama kota kakak untuk kami cek ongkos kirimnya")
            return [UserUtteranceReverted()]
        return [SlotSet('Lokasi',lokasi)]

class ActionReplyJawabOngkir(Action):
    def name(self):
        return 'action_reply_ongkir'

    def run(self, dispatcher, tracker, domain):
        lokasi = tracker.get_slot('Lokasi')
        logistik = next(tracker.get_latest_entity_values("Logistik"), None)
        if not logistik:
            dispatcher.utter_message("Logistik apa yang ingin kakak gunakan ? Saat ini kami menyediakan TIKI, JNE, dan POS")
            return []
        elif logistik.lower() not in ['jne','tiki','pos']:
            dispatcher.utter_message("Logistik yang kakak masukan salah. Silahkan di ulangi")
            return []
        else:
            conn = http.client.HTTPSConnection("api.rajaongkir.com")
            headers = { 'key': "040823d1664ea0661eb227d54a7f87d0" }
            header = { 'key': "040823d1664ea0661eb227d54a7f87d0",'content-type': "application/x-www-form-urlencoded" }
            conn.request("GET", "/starter/city?id=", headers=headers)
            res = conn.getresponse()
            data = res.read()
            data_convert = data.decode("utf-8")
            json_string = json.loads(data_convert)
            result = jsonpath.jsonpath(json_string,"$..results[?(@.city_name=='"+ lokasi.title() +"')]")
            result_id = jsonpath.jsonpath(result,"$..city_id")
            if result_id is False:
                dispatcher.utter_message("Maaf kak nama kota salah")
            else:
                city_id = ''.join(result_id)
                if len(city_id) > 3:
                    result_id = [d['city_id'] for d in result]
                    result_id.pop(0)
                city_id = ''.join(result_id)
                payload = 'origin=55&destination=' + city_id + ' &weight=1000&courier=' + logistik.lower() + ''
                conn.request("POST", "/starter/cost", payload, header)
                resu = conn.getresponse()
                datas = resu.read()
                data_convert = datas.decode("utf-8")
                json_strings = json.loads(data_convert)
                service = jsonpath.jsonpath(json_strings,"$..results..service")
                str_service = ' '.join(str(service))
                cost = jsonpath.jsonpath(json_strings,"$..results..cost..value")
                etd = jsonpath.jsonpath(json_strings,"$..results..cost..etd")
                str_estimated = ' '.join(etd)
                dispatcher.utter_message(str(str_estimated))
                dispatcher.utter_message("Untuk jenis servis yang tersedia, ongkos kirim dan estimasi sampai silahkan baca menurun sesuai data dibawah ini ya kak :)")
                dispatcher.utter_message(str(str_service))
                dispatcher.utter_message(str(cost))
                dispatcher.utter_template("utter_estimated",tracker,Estimated=str(str_estimated))
        return []
            





             









        
    