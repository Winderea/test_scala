from FlipKraft.API.views.BaseView import BaseView
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
import logging
import datetime
import pytz
from FlipKraft.API.serializers import GameSerializer, GameGetSerializer, GameGetIDSerializer
from FlipKraft.API.models import Projects
from FlipKraft.API.models import Games

# Mon projet de fin d'étude, est une plateforme de création de jeu de carte personnalisé, une fois le jeu aboutis, on peut lancer des parties sur la plateforme pour jouer entre amis
# Dans mon projet de fin d'étude j'ai été amené, entre autre, à gérer la création de salle de lobby pour l'hébergement d'une partie de jeu de carte en ligne.
# La classe GameView s'occupe de la gestion des requêtes http envoyé à notre API


class GameView(BaseView):

    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    ## La partie dont je suis le moins fier est la première fonction get. 
    ## L'idée, c'est que lorsque l'api reçoit un GET sur la route /api/games, la requête renvoie toutes les parties hébergés, et dont leur date de création est inférieur à 10 minutes
    ## Si une partie a été créée il y a plus de 10min la requête doit également se charger de mettre la salle d'attente en statut fermé.
    ## La fonction si dessous remplie bien les contraintes, en revanche, je m'y prends ici en faisant 2 appels à la base de donnée
    ## 

    def get(self, request, format=None):
        games_id = Games.objects.all().filter(status=True) # Premier appel, afin de récupérer toutes les parties ouvertes, cette ligne me retourne une liste de parties
        if games_id:
            for game in games_id:
                if datetime.datetime.utcnow().replace(tzinfo=pytz.UTC) > game.expiration_date:
                    game.status = False
                    game.save()## Je vérifie le statut de chacune des parties, et si leur date de création est supérieure à 10 minutes, puis je sauvegarde les modifications en base de donnée
            games_id = Games.objects.all().filter(status=True)# Ici je refait un second appel pour récupérer à nouveau toutes  les parties
            serializer = GameGetSerializer(games_id, many=True)# Serialisation
            return Response(serializer.data, status=200)# Envoie des données dans la requête.
        return Response(status=200)
        ## Après reflexion plutot que de faire 2 appels à la base de donnée, j'aurais simplement du, une fois les modifications faites sur la liste, récupéré ceux dont le status était open, sans passer par un second appel à la BDD
        
    
    
    
    
    
    
    ## La partie dont je suis le plus fier est la fonction get ci dessous
    ## Cette fonction permet à un joueur, une fois qu'il a rejoint une partie de récupérer toutes les ressources nécessaire pour jouer au jeu avec son ami sans avoir besoin de posséder le jeu au préalable
    ## Les nested serializer de Django Rest sont particulièrement efficaces pour ce cas de figure

    def get(self, request, pk=None, format=None):
        game = Games.get_game(pk) #Ici on récupère le lobby
        if game:
            serializer_context = {'request': request}
            serializers = GameGetIDSerializer(game, context=serializer_context)# On crée le nested serializer, qui prend toutes les informations relatives à un jeu de carte.
            return Response(serializers.data, status=200)# On renvoit le tout dans la réponse
        return Response("Game not found", status=404)

## Le nested serializer
class GameGetIDSerializer(serializers.HyperlinkedModelSerializer):

    project = ProjectDetailSerializer(source='fk_id_project', read_only=True) ## Cette ligne est particulièrement importante, elle signifie que pour le champs "project" du serializer on veut insérer un autre serializer qui correspond à un jeu de carte

    class Meta:
        model = Games
        fields = (
            'id',
            'name',
            'status',
            'author',
            'project'
        )
## le serializer qui correspond au jeu de carte        
    class ProjectDetailSerializer(serializers.HyperlinkedModelSerializer):
    """ Serializer for a specific Project class """
    fk_user = UserSerializer(read_only=True)
    cards = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    ressources = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    phases = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Projects
        fields = (## Tous les champs à partir d'ici seront donc inséré dans le champ project du GameGetIDSerializer.
            'id',
            'fk_user',
            'name',
            'async_game',
            'turn_game',
            'description',
            'min_player',
            'max_player',
            'cards',
            'ressources',
            'creation_date',
            'phases'
        )

