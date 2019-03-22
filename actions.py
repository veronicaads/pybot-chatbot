from rasa_core_sdk import Action
from rasa_core_sdk.events import SlotSet
from rasa_core_sdk.events import UserUtteranceReverted
from rasa_core_sdk.events import AllSlotsReset
from rasa_core_sdk.events import Restarted

import psycopg2
DSN = "postgres://postgres:root@localhost:5432/skripsweet"

import .apicall


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
                curs.execute(f"""SELECT stock,material_hp,harga FROM produk WHERE concat(merkhp, ' ', tipehp) LIKE '%{jenishp.lower()}%' """)
                result = curs.fetchall()
                if result is not None:
                    dispatcher.utter_template("utter_reply_ketersediaan_produk_tersedia",tracker,Jenis_HP=jenishps)
                    for result_row in result:
                        stock = result_row[0]
                        if int(stock) > 0:
                            dispatcher.utter_template("utter_reply_ketersediaan_produk_tersedia_list",tracker,Material=result_row[1],Harga=result_row[2])           
                        else:
                            dispatcher.utter_template("utter_reply_ketersediaan_produk_tidak_tersedia",tracker,Jenis_HP=jenishp)    
                else:
                    dispatcher.utter_template("utter_reply_ketersediaan_produk_tidak_tersedia",tracker,Jenis_HP=jenishp)
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
                curs.execute(f"""SELECT lama_pengerjaan FROM produk WHERE concat(merkhp, ' ', tipehp) LIKE '%{jenishp.lower()}%' AND material_hp LIKE '%{materials.lower()}%'  """)
                result = curs.fetchone()
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
                curs.execute(f"""SELECT harga FROM produk WHERE concat(merkhp, ' ', tipehp) LIKE '%{jenishp.lower()}%' AND material_hp LIKE '%{materials.lower()}%'  """)
                result = curs.fetchone()
                if result is None:
                    dispatcher.utter_message("Hasil tidak ditemukan. Maaf kak :(")
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
                    curs.execute(f"""SELECT namabank,norek,atasnama FROM bank """)
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
                    curs.execute(f"""SELECT namabank,norek,atasnama FROM bank WHERE namabank LIKE '%{namabank.lower()}%' """)
                    result = curs.fetchone()
                    dispatcher.utter_template("utter_reply_bank_available",tracker,NamaBank=result_row[0],Norek=result_row[1],AtasName=result_row[2])
                    return []

class ActionReplyInfoOlshop(Action):
    def name(self):
        return 'action_reply_lokasi_tersedia' 
    
    def run(self, dispatcher, tracker, domain):
        with psycopg2.connect(DSN) as conn:
            with conn.cursor() as curs:
                curs.execute(f"""SELECT kota_olshop, provinsi_olshop FROM info_olshop """)
                result = curs.fetchone()
                dispatcher.utter_template("utter_reply_lokasi_olshop",tracker,Kota=result[0],Provinsi=result[1])
                return []

class ActionReplyInfoLogistik(Action):
    def name(self):
        return 'action_reply_logistik_tersedia' 
    
    def run(self, dispatcher, tracker, domain):
        with psycopg2.connect(DSN) as conn:
            with conn.cursor() as curs:
                curs.execute(f"""SELECT namalogistik FROM logistik """)
                result = curs.fetchall()
                if result is not None:
                    dispatcher.utter_message("Saat ini kami menggunakan jasa pengiriman : ")
                    for result_row in result:
                        dispatcher.utter_template("utter_ketersediaan_logistik",tracker,NamaLogistik=result_row[0])
                else:
                    dispatcher.utter_message("Hasil tidak ditemukan ")
        return []

             









        
    