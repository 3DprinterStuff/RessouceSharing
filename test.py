import json
import unittest
from flask import Flask,request,redirect

class InitialTests(unittest.TestCase):
    def test(self):
        import server as serverLib
        import client as clientLib

        app = Flask(__name__)

        tools = serverLib.Category("Werkzeug")
        materials = serverLib.Category("materialien")
        trash = serverLib.Category("Müll")

        server = serverLib.Server()


        me = serverLib.Actor("me")
        me.desires.extend([serverLib.Query("Topf"),
                                 serverLib.Query("Fotoapperat",categories=[tools]),
                                 serverLib.Query("Satelitenschüssel",categories=[materials]),
                                 serverLib.Query("Zange",categories=[tools]),
                                 serverLib.Query("Rettungsdecke",categories=[materials]),
                                 serverLib.Query("generator-elektromotor",categories=[materials]),
                                 serverLib.Query("Stecker",categories=[materials])
                                ])
        me.inventory.extend([serverLib.Thing("Aluminium",categories=[materials,trash]),
                                  serverLib.Thing("Kupfer",categories=[materials,trash]),
                                  serverLib.Thing("Kühler",categories=[materials,trash]),
                                  serverLib.Thing("Computer",categories=[materials,trash]),
                                  serverLib.Thing("Platinen",categories=[materials,trash]),
                                  serverLib.Thing("Plastik",categories=[materials,trash]),
                                  serverLib.Thing("Säuren",categories=[materials,trash]),
                                  serverLib.Thing("Festplattenmagneten",categories=[materials]),
                                  serverLib.Thing("Festplattenmotoren",categories=[materials]),
                                 ])
        server.users[me.name] = me

        # create A.
        personA = serverLib.Actor("A.")
        server.users[personA.name] = personA

        # create K.
        personK = serverLib.Actor("K.")
        server.users[personK.name] = personK

        # create R.
        personR = serverLib.Actor("R.")
        server.users[personR.name] = personR

        # create Test
        somebodyElse = serverLib.Actor("hurk")
        somebodyElse.IaddToInventory(somebodyElse, [serverLib.Thing("Topf"),
                                                    serverLib.Thing("Vogelhaus"),
                                                    serverLib.Thing("Schaukel"),
                                                    serverLib.Thing("Katzenstreu",categories=[materials])
                                                   ])
        server.users[somebodyElse.name] = somebodyElse

        print("--- lonely ")
        serverLib.findRessources(me)

        print("--- with friends ")
        me.IaddContact(somebodyElse)
        serverLib.findRessources(me)

        print("--- after statechage")
        somebodyElse.IaddToInventory(somebodyElse,[serverLib.Thing("Bohrer",categories=[tools])])
        shovel = serverLib.Thing("Schaufel")
        somebodyElse.IaddToInventory(somebodyElse,[shovel])
        somebodyElse.IaddToInventory(somebodyElse,[serverLib.Thing("Handkarren")])

        desire = serverLib.Query("Bohrer")
        me.IaddDesires(me,[desire])
        serverLib.findRessources(me)

        print("--- after item edit")
        shovel.IchangeCategories(somebodyElse,[tools])
        serverLib.findRessources(me)

        print("--- after transfer")
        somebodyElse.inventory.remove(shovel)
        shovel.holder = None
        me.IaddToInventory(me,[shovel])
        serverLib.findRessources(me)

        print("--- after adding sink")
        sink = serverLib.Actor("Wertstoffhof")
        server.users[sink.name] = sink
        sink.IaddDesires(sink,[serverLib.Query("Kupfer"),
                               serverLib.Query("Platinen"),
                               serverLib.Query(None,categories=[trash])])
        serverLib.findRessources(me)

        print("--- after connecting to sink")
        me.IaddContact(sink)
        serverLib.findRessources(me)

        personD = serverLib.Actor("D.")
        server.users[personD.name] = personD

class LoadingTests(unittest.TestCase):
    def test1(self):
        import server as serverLib
        
        server = serverLib.Server("test1")
        self.assertEqual(len(server.users),3)
        self.assertEqual(len(server.users["me"].inventory),4)

if __name__ == '__main__':
    unittest.main()
