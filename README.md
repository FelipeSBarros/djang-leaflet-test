# Prototype of a django project using leaflet

### Criando ambiente de desenvolvimento, projeto e nossa app:
Vamos criar um ambiente virtual python e instalar a framework django, para cria ro sistema, assim como alguns modulos como `jsonfield`, que nos vai habilitar a criação de campos `json` em nossa base de dados, assim como `django-geojson`. Este ultimo, que depende do `jsonfield` cria uma instancia de dados geográficos mais comuns, baseando-se e json. Por isso o nome `geojson`. 
O uso desses dois módulos nos permitirá o desenvolvimento de um systema de gestão de dados geográficos sem a necessidade de termos instalado um sistema de gerenciamento de dados geográficos, como o PostGis. Sim, nosso sistema será bem limitado a algumas tarefas. Mas en contrapartida, poderemos desenvolvê-lo e implementar soluções "corriqueiras" de forma facilitada. 

Nosso projeto se chamará de mapProj. E nele vou criar uma app, chamada `core`. Essa organização e nomenclartura usada, vem das sugestões do [Henrique Bastos](). Afinal, o sistema está nascendo. Ainda que eu tenha uma ideia do que ele será, é interessante iniciar com uma app "genérica" e a partir do momento que o sistema se torne complexo, poderemos desacoplá-lo em diferentes apps.

```python
python -m venv .djleaflet
pip install --upgrade pip
pip install django jsonfield django-geojson
django-admin startproject mapProj .
cd mapProj
manage startapp core
manage migrate
manage createsuperuser
```

#### Adicionando os módulos e a app ao projeto

Agora é adicionar ao `settings.py`, a app criada e os módulos que usaremos.

```python
# setting.py
INSTALLED_APPS = [
    ...
    'mapProj.core',
    'djgeojson',
]
```

### Criando a base de dados

Ainda que eu concorde com o Henrique Bastos, de que a visão de começar os projetos django pelo `models.py` é um tanto "perigosa", por colocar ênfase em uma parte da app e, em muitos casos, negligenciar varios outros atributos e ferramentas que o django nos oferece. Mas como o objetivo deste artigo não é explorar todo o potencial do django, mas sim apresentar uma solução simples no desenvolvimento e implementação de um sistema de gestão de dados geográficos, vou seguir assim, mesmo.

Em `models.py` usaremos instancias de altonível que o django nos brinda para criar e configurar alguns comportamentos da nossa base de dados e as respectivas tabelas.

Vejam que antes de tudo, eu importo de `djgeojson` a classe `PointField`. O que o `djgeojson` fez foi criar uma classe [com estrutura de dados goegráfico] de alto nível em json, fazendo com que possamos trabalhar com o mesmo, sem ter que criá-lo "na unha". Isso além de proporcionar métodos e sistemas de validação, etc.
Mais informações sobre o [`djgeojson`](https://pypi.org/project/django-geojson/):

> All geometry types are supported and respectively validated : GeometryField, PointField, MultiPointField, LineStringField, MultiLineStringField, PolygonField, MultiPolygonField, GeometryCollectionField.

Como estou fazendo um sistema multipropósito, vou tentar manter bem genérico. A ideia é que vocês possam imaginar o que adequar para um sistema especialista na sua área de interesse. Vou criar, então, uma tabela para mapear "fenómenos" (quaisquer). Eses terão os campos "nome", "data", "hora" e uma geometria, na qual vou usar `PointField`. Ficando assim:

```python
# models.py
from django.db import models
from djgeojson.fields import PointField


class Fenomeno(models.Model):

    name = models.CharField(max_length=100, 
                            verbose_name='Fenomeno mepado')
    data = models.DateField(verbose_name='Data da observação')
    hora = models.TimeField()
    geom = PointField()
```

Pronto, já temos o modelo da 'tabela de dados "geográficos"'. Lembrando que no temos todo o poder de uma base de dados, mas sim, uma construção em json para minimamente armazenar y validar dados geográficos.
Contudo, esse modelo aidna não foi "commitado" para a nossa base. Para isso:

```python
manage makemigrations
manage migrate
```

#### Mas ~~antes,~~ [e o] teste~~!~~?

Pois é, eu adoraria apresentar isso usando a abordagem *Test Driven Development (TDD)*. Mas, talvez pela falta de prática, conheciemnto e etc, vou apenas apontar onde e como eu testaria esse sistema. Faço isso como uma forma de estudo, mesmo. Também me pareceu complicado apresentar a abordagem TDD em um artigo, já que a mesma se faz de forma inscremental.

#### Sobre TDD

Soube do *TDD* em um encontro no Rio de Janeiro, chamado [DOJO](). Ainda que eu só tenha tido a oportunidade de ir uma vez, e do fato de quando eu ter ido, termos feito o *Code Dojo* em JavaScript, me interessou bastante essa abordagem. Claro, com o Henrique Bastos e toda a comunidade do [*Welcome to The Django*]() ví que essa abordagem é mais filosófica que técnica. É praticamente "Chora agora, ri depois", mas sem a parte de chorar. Pq com o tempo as coisas ficam mais claras... Alguns pontos:

* O erro não é para ser evitado. Logo, 
* Enfrente o Erro, traga ele pra perto. Ele é seu amigo :heart:
* Teste o comportamento esparado e não cada elemeto do sistema 

Sem mais delongas:

#### O que testar?

Vamos usar o arquivo `tests.py` e  criar nossos testes lá.
Ao abrir vocês vão ver que já está o comando importando o `TestCase`.

> Mas o que vamos testar?

Como o objetivo do projeto é criar um sistema qualquer com dados geográficos, vou me ater em:
1. testar a inserção de dados e 
2. existência de um campo reservado para dados geográficos validando se o mesmo é uma instância `djgeojson`. Mas fico aberto à críticas e sugestões :)

Para ambos os casos, vou criar objeto do meu modelo `Fenomeno`, no `setUp`, para não ter que criá-lo sempre que for fazer um teste simulando a interação com a base de dados. E nessa carga de dados geográficos, fica claro a estrutura dos dados `djgeojson`, um dicionário com a chave `type` e `coordinates`, sendo a primeira responsável por identificar o tipo do dado e a última, uma lista de dois valores numéricos.

```python
from django.test import TestCase
from mapProj.core.models import Fenomeno


class ModelGeomTest(TestCase):
    def setUp(self):
        self.fenomeno = Fenomeno.objects.create(
            name='Arvore',
            data='2020-11-06',
            hora='09:30:00',
            geom={'type': 'Point', 'coordinates': [0, 0]}
        )

    def test_create(self):
        self.assertTrue(Fenomeno.objects.exists())

    def test_geom_is_Point(self):
        self.assertEqual(self.fenomeno.geom.get("type"), "Point")

```
:warning: Reparem que: 
1. Para realizar o teste eu preciso importar o models da app em questão;
1. No `test_create()` eu testo se existem objetos inseridos no model `Fenomeno`; Já no `test_geom_is_Point()`, eu testo se o Tipo de dado geográfico é o esperado.


#### Registrando modelo no admin

Para facilitar, vou usar o django-admin. Trata-se de uma aplicação já criada onde basta registrar os modelos e views que estamos trabalhando para termos uma interface "frontend" genérica.

```python
#admin.py
from django.contrib import admin
from mapProj.core.models import Fenomeno

admin.site.register(Fenomeno)

```

#### Add statics urls

```python
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR
```