import re
import requests

class RajaOngkir:
    def __init__(self, apikey, service='starter'):
        self.apikey = apikey
        self.headers = {'key':self.apikey}
        self.BASEURL = "http://rajaongkir.com/api/"
        self.URLSTARTER = service+"/"


    def getCitiesId(self, kotaid="", provinsiid=""):
        
        """Mencari data tentang kota, bila kotaid dan provinsiid id kosong
        akan menampilkan seluruh kota yang ada di database rajaongkir.com"""
        
        self.paramskota = {"id":kotaid,"province":provinsiid}
        bukaurl = requests.get(self.BASEURL+self.URLSTARTER+"city", params=self.paramskota,
        headers = self.headers)
        self.data = bukaurl.json()
        return self.data

    def getCityId(self, kota):
        """Mencari id dari suatu kota dengan masukan namakota, dan keluaran angka
        berupa id kota"""
        
        self.kota = kota.lower()
        daftar_kota = self.getCitiesId()["rajaongkir"]["results"]
        for kota in daftar_kota:
            if re.search(self.kota, kota["city_name"].lower()):
                return kota['city_id']
           
    def getCostData(self, dari, tujuan, berat="1000", kurir="jne"):
        
        """Mendapatkan data Harga
        Parameter:
        dari = kota asal
        tujuan = kota tujuan
        berat = dalam gram
        kurir = """
        
        
        self.dari = str(self.getCityId(dari))
        
        self.tujuan = str(self.getCityId(tujuan))
        self.berat = int(berat)
        self.kurir = kurir
        self.params_cost =   {  "origin":self.dari,
                                "destination": self.tujuan,
                                "weight": self.berat,
                                "courier": self.kurir
                                }
        bukaurla = requests.post(self.BASEURL+self.URLSTARTER+"cost", data= self.params_cost ,
        headers = self.headers)
        return bukaurla.json()
        
    def rapikanDataCost(self, data):
        """Merapikan keluaran untuk cost
        
        parameter:
        data = json hasil keluaran request ke rajaongkir API
        """
        
        data_harga = data['rajaongkir']['results'][0]['costs']
        perkiraan = [x['cost'][0]['etd'] for x in data_harga]
        harga = [x['cost'][0]['value'] for x in data_harga]
        deskripsi = [x['description'] for x in data_harga]
        service = [x['service'] for x in data_harga]
        jumlah = len(data_harga)
        keluaran = []
        for x in range(jumlah):
            hasil = "Layanan = %s(%s)\nPekiraan Sampai =  %s hari\nHarga = %s"%(
            service[x],deskripsi[x],perkiraan[x],harga[x])
            keluaran.append(hasil)
        return  "\n\n".join(keluaran)
        
    def rapikanDataHeader(self, data):
        """Merapikan keluaran untuk header
        
        parameter:
        data = json hasil keluaran request ke rajaongkir API
        """
        
        data_origin = data['rajaongkir']['origin_details']
        data_origin_kota = data_origin['city_name']
        data_origin_province = data_origin['province']
        data_dest = data['rajaongkir']['destination_details']
        data_dest_kota = data_dest['city_name']
        data_dest_province = data_dest['province']
        data_berat =data['rajaongkir']['query']['weight']
        data_layanan = data['rajaongkir']['query']['courier']
        return "Pengiriman dari %s,%s ke %s,%s dengan berat %s menggunakan layanan %s"%(
        data_origin_kota, data_origin_province, data_dest_kota, data_dest_province,
        data_berat, data_layanan.upper()
        )
        
    def hitungOngkos(self, kotadari, kotake, berat=1000, kurir="jne"):
        """Method untuk hitung ongkos kirim, dengan keluaran string, 
        bkan format json lagi
        
        kotadari = dari
        kotake = ke
        berat = berat kiriman
        kurir = kurir yang akan anda gunakan"""
        
        try:
            data= self.getCostData(kotadari, kotake, berat, kurir)
            data_cost_rapi = self.rapikanDataCost(data)
            data_header = self.rapikanDataHeader(data)
            return "%s\n\n%s\n\n\nVia Rajaongkir.com"%(
                     data_header, data_cost_rapi
                       )
        except ValueError:
            return "Data yang anda masukkan tidak ditemukan"
        
if __name__ == "__main__":
    rajaongkir = RajaOngkir(your-apikey-here)
    print rajaongkir.hitungOngkos("semarang", "Surakarta")