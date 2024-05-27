#import
import numpy as np


ProductType = {
    "lait":{},
    "oeuf":{},
    "beurre":{},
    "crème":{},
    "fromage":{},
    "Goûter":{},
    "Fruit":{},
    "légumes":{}
               }

Marques = ["Marque1","Marque2","Marque3","Marque4"]
#Constantes
Date = 0
grande_période = 14
moving_average_size = 5*grande_période
SurStock = 1.0
DélaiDon = 2
#agent du modèle
class Supplier():
    
    def commande(self,productype,quantité):
        return Product(Date + grande_période + 1.5*np.random.random(),productype,np.random.normal(0,1),quantité)

class Supermarket():
    def __init__(self,Taille,Marque,id):
        self.stock = [] #liste des produits en magasin
        self.stockoverview = {}
        for name in ProductType.keys() :
            self.stockoverview[name] = 0
        self.StockDons = {}
        for name in ProductType.keys() :
            self.StockDons[name] = 0
        self.clients = []
        self.BanqueDeDons = []
        self.taille = Taille
        self.Marque = Marque
        self.id = id
        self.péremption_max = 0
        self.quantitéRupture = 0
        self.ventes = 0
        self.dons = 0
        self.Demande = {} #enregistre la demande des clients à chaque période de référence
        for name in ProductType.keys() :
            self.Demande[name] = []
        self.supplier = Supplier()
     
  

    def Inventaire(self):
        """Fait l'inventaire sans prendre en compte les lots de produits"""
        self.stockoverview = {}
        for name in ProductType.keys() :
            self.stockoverview[name] = 0

        self.StockDons = {}
        for name in ProductType.keys() :
            self.StockDons[name] = 0


        for produit in self.stock : 
            if not(produit.estpérimé()):
                if produit.Type in self.stockoverview.keys() : 
                    self.stockoverview[produit.Type] += produit.quantité
                else : self.stockoverview[produit.Type] = produit.quantité
            elif not(produit.DateLimiteDeConsomation < Date - DélaiDon) :
                self.StockDons[produit.Type] += produit.quantité
            if produit.DateLimiteDeConsomation > self.péremption_max : 
                self.péremption_max = produit.DateLimiteDeConsomation

    def actualiseStock(self,produit,quantité,Dons = False) : 
        """Actualise le stock du produit voulu et de la quantité concernée en comsomant les dates les plus avancées"""
        
        délai = 0
        if Dons :
            délai = DélaiDon
            self.StockDons[produit] -= quantité
        else : 
            self.stockoverview[produit] -= quantité

        while quantité > 0.1 : 
            péremption_min,indice = self.péremption_max,-1
            
            for i in range(len(self.stock)) : 

                if self.stock[i].Type == produit and (self.stock[i].DateLimiteDeConsomation <= péremption_min) and not(self.stock[i].DateLimiteDeConsomation < Date - délai): 
                    péremption_min = self.stock[i].DateLimiteDeConsomation
                    indice = i
            if indice == -1 : raise Exception(str(indice)+ " "+str(self.StockDons[produit])+ " " + str(quantité) +" "+ str(self.id)+" "+str(délai)+""+str(Dons))
            if self.stock[indice].quantité > quantité + 0.1 : 
                self.stock[indice].quantité -= quantité
                quantité = 0
            else : 
                quantité-= self.stock[indice].quantité
                self.stock.pop(indice)


    def Vente(self):
        """Effectue les ventes sur la période de référence"""
        
        for client in self.clients : 
            for i in range(len(client.Besoin)) : 
                produit,quantité = list(ProductType.keys())[i],client.Besoin[i] 
                
                if self.stockoverview[produit] <= 0.1 or quantité <= 0.1 :
                    pass
                elif self.stockoverview[produit] >= quantité : 
                    self.actualiseStock(produit,quantité)
                    self.ventes += quantité
                else : 
                    
                    self.quantitéRupture += quantité - self.stockoverview[produit] 
                    self.ventes += self.stockoverview[produit]
                    self.actualiseStock(produit,self.stockoverview[produit])

    def Dons(self):
        """Effectue les dons sur la période de référence"""
        
        for banque in self.BanqueDeDons : 
            for i in range(len(banque.Besoin)) : 
                produit,quantité = list(ProductType.keys())[i],banque.Besoin[i] 
                if quantité <= 0 : 
                    pass
                elif self.StockDons[produit] <= 0.1 :
                    pass
                elif self.StockDons[produit] >= quantité : 
                    self.actualiseStock(produit,quantité,Dons = True)
                    banque.Besoin[i] -= quantité
                    self.dons += quantité
                else : 
                    self.dons += self.StockDons[produit]
                    self.actualiseStock(produit,self.StockDons[produit],Dons= True)
                    banque.Besoin[i] -= self.StockDons[produit]

    def EnregistrementDemande(self): 
        """Enregistre la demande des clients à l'heure actuelle"""
        for key in self.Demande.keys() : 
            self.Demande[key] += [0]
        for client in self.clients : 
            for i in range(len(client.Besoin)) : 
                produit,quantité = list(ProductType.keys())[i],client.Besoin[i]
                if produit in self.Demande.keys() : 
                    self.Demande[produit][-1] += quantité
                else : 
                     self.Demande[produit] = [quantité]

    def Commande(self):
        """Effectue les commandes aux suppliers"""
        for key in self.Demande.keys() : 
            self.stock.append(self.supplier.commande(key,SurStock*grande_période*np.average(self.Demande[key][-moving_average_size:])- self.stockoverview[key]) )

    def Rebut(self):
        """met au rebut les articles abîmés et périmé"""
        rebut = {}
        for name in ProductType.keys() :
            rebut[name] = 0
        n = 0
        for i in range(len(self.stock)) : 
            product = self.stock[i - n]
            if product.estpérimé() : 
                rebut[product.Type] += product.quantité
                self.stock.pop(i - n)
                n += 1
        return rebut
def temps():
    global Date
    Date += 1

class BanqueAlimentaire():
    def __init__(self,c,v):
        self.constants = v*np.random.random(len(ProductType)) + c
        self.Besoin = np.ones((len(ProductType)))*self.constants
        self.ARcoef = np.random.random((AR,len(ProductType))) -0.5
        self.MAcoef = np.random.random(size=(MA,len(ProductType))) -0.5
        self.randomness = np.random.normal(0,1,size=(MA+1,len(ProductType)))
        self.historique = np.ones((AR,len(ProductType)))*self.constants
        self.BesoinCopy = self.Besoin[:]
    def ARMA(self):
        #roll de l'historique
        self.historique[:-1,:] = self.historique[1:,:]
        self.historique[-1,:] = self.BesoinCopy
        #roll de l'aléatoire 
        self.randomness[:-1,:] = self.randomness[1:,:]
        self.randomness[-1,:] =np.random.normal(0,1,size=len(ProductType))
        #nouveaux besoins
        
        self.BesoinCopy = np.sum(self.historique*self.ARcoef + self.randomness[:-1]*self.MAcoef,axis=0) + self.randomness[-1] + self.constants
        self.Besoin = self.BesoinCopy[:]


AR, MA = 2,2
class Customer:

    def __init__(self,c,v):
        self.constants = v*np.random.random(len(ProductType)) + c
        self.Besoin = np.ones((len(ProductType)))*self.constants
        self.ARcoef = np.random.random((AR,len(ProductType))) -0.5
        self.MAcoef = np.random.random(size=(MA,len(ProductType))) -0.5
        self.randomness = np.random.normal(0,1,size=(MA+1,len(ProductType)))
        self.historique = np.ones((AR,len(ProductType)))*self.constants
    def ARMA(self):
        #roll de l'historique
        self.historique[:-1,:] = self.historique[1:,:]
        self.historique[-1,:] = self.Besoin
        #roll de l'aléatoire 
        self.randomness[:-1,:] = self.randomness[1:,:]
        self.randomness[-1,:] =np.random.normal(0,1,size=len(ProductType))
        #nouveaux besoins
        
        self.Besoin = np.abs(np.sum(self.historique*self.ARcoef + self.randomness[:-1]*self.MAcoef,axis=0) + self.randomness[-1] + self.constants)

#éléments échangés 
class Product():
    def __init__(self,DateLimiteDeConsomation,Type,Value,Quantité) : 
        self.DateLimiteDeConsomation = DateLimiteDeConsomation
        self.Type = Type
        self.Value = Value
        self.quantité = Quantité
        self.Périssable = True
    def estpérimé(self):
        if self.Périssable == True : 
            return self.DateLimiteDeConsomation < Date
        return False
    
#hypothèses : 
#La demande est spécifique à chaque supermarché 
#Les Besoins des consomateurs son des ARMA(2,2)
#Les banques alimentaire ne font appel qu'a une marque => intérêt de notre solution en utilisant plusieur marques 
#à faire 
#définier un modèle de prix 
#définir un modèle de demande 
#initialisation du modèle 
Magasins = []
Magasins
#période d'observation de la demande ( permet d'initier les prédictions des magasins)

#On passe le système dans une boucle d'une durée d'un moi 

