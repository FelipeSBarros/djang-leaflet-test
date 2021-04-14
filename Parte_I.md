# Criando um sistema Geo super simples com Django

Por super simples, entende-se: 
* Um sistema sem a necessidadde da instalação e configuração de uma base de dados PostgreSQL/GIS;
* Um sistema clásico tipo *Create*, *Update*, *Delete* (CRUD) para dados geográficos;
* Um sistema que não demande operações e consultas espaciais;

### Visão geral de proposta:
Vamos criar um ambiente virtual python e instalar a framework django, para criar o sistema, assim como alguns módulos como `jsonfield`, que nos vai habilitar a criação de campos `json` em nossa base de dados, assim como `django-geojson`. Este ultimo, que depende do `jsonfield` cria uma instância de dados geográficos, baseando-se e json. Por isso o nome [`geojson`](https://geojson.org/). 
O uso desses dois módulos nos permitirá o desenvolvimento de um sistema de gestão de dados geográficos sem a necessidade de termos instalado um sistema de gerenciamento de dados geográficos, como o PostGIS. Sim, nosso sistema será bem limitado a algumas tarefas. Mas en contrapartida, poderemos desenvolvê-lo e implementar soluções "corriqueiras" de forma facilitada. 

Nosso projeto se chamará de mapProj. E nele vou criar uma app, chamada `core`. Essa organização e nomenclartura usada, vem das sugestões do [Henrique Bastos](https://henriquebastos.net/desmistificando-o-conceito-de-django-apps/). Afinal, o sistema está nascendo. Ainda que eu tenha uma ideia do que ele será, é interessante iniciar com uma app "genérica" e a partir do momento que o sistema se torne complexo, poderemos desacoplá-lo em diferentes apps.

### Criando ambiente de desenvolvimento, projeto e nossa app:

```python
python -m venv .djleaflet # cria ambiente virtual python
# uma vez ativado o ambiente virtual:
pip install --upgrade pip
pip install django jsonfield django-geojson
django-admin startproject mapProj . # criando projeto
cd mapProj
manage startapp core # criando app dentro do projeto
manage migrate # criando a base de dados incial
manage createsuperuser # criando superusuário
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

Perceba que para pode acessar as classes de alto nível criadas pelo pacote `djgeojson`, teremos que adicioná-lo ao `INSTALLED_APPS` do `settings.py`.

### Criando a base de dados

Ainda que eu concorde com o Henrique Bastos, de que a visão de começar os projetos django pelo `models.py` é um tanto "perigosa", por colocar ênfase em uma parte da app e, em muitos casos, negligenciar vários outros atributos e ferramentas que o django nos oferece, irei negligenciar sua abordagem. Afinal, estamos criando um sistema para a gestão de dados geográficos... **dados geográficos**.
Enfim, o objetivo deste artigo não é explorar todo o potencial do django, mas sim apresentar uma solução simples no desenvolvimento e implementação de um sistema de gestão de dados geográficos, vou seguir assim, mesmo.

Em `models.py` usaremos instâncias de alto nivel que o django nos brinda para criar e configurar os campos e as tabelas que teremos em nosso sistema, bem como alguns comportamentos do sistema, como o processo de sanitização dos dados.

Vejam que antes de tudo, eu importo de `djgeojson` a classe `PointField`. O que o `django-geojson` fez foi criar uma classe [com estrutura de dados goegráfico] de alto nível que no banco será armazenado em um campo json:

> All geometry types are supported and respectively validated : GeometryField, PointField, MultiPointField, LineStringField, MultiLineStringField, PolygonField, MultiPolygonField, GeometryCollectionField.

Ao fazer isso, poderemos trabalhar com esse dado como se fosse um dado geográfico, com métodos e sistemas de validação desse campo. Contudo, nem tudo são flores: **Consultas e operações espaciais não são contemplados**. Para tais casos, vocÇe precisará do PstGIS.
Mais informações sobre o [`djgeojson`](https://pypi.org/project/django-geojson/)

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
Contudo, esse modelo ainda não foi "commitado"/"registrado" para/na a nossa base. Para isso:

```python
manage makemigrations
manage migrate
```
O `makemigrations` analisa o `models.py` e o compara com a versão anterior identificando as alterações e criando um arquivo que será executado pelo `migrate`, aplicando tais alterações ao banco de dados.

#### Mas ~~antes,~~ [e o] teste~~!~~?

Pois é, eu adoraria apresentar isso usando a abordagem *Test Driven Development (TDD)*. Mas, talvez pela falta de prática, conhecimento e etc, vou apenas apontar onde e como eu testaria esse sistema. Faço isso como uma forma de estudo, mesmo. Também me pareceu complicado apresentar a abordagem TDD em um artigo, já que a mesma se faz de forma incremental.

##### Sobre TDD

Soube do *TDD* em um encontro no Rio de Janeiro, chamado [DOJORio](https://github.com/dojorio). Ainda que eu só tenha tido a oportunidade de ir uma vez, e do fato de quando eu ter ido, termos feito o *Code Dojo* em JavaScript, me interessou bastante essa abordagem. Claro, com o Henrique Bastos e toda a comunidade do [*Welcome to The Django*](https://medium.com/welcome-to-the-django/o-wttd-%C3%A9-tudo-que-eu-ensinaria-sobre-prop%C3%B3sito-de-vida-para-mim-mesmo-se-pudesse-voltar-no-tempo-d73e516f911c) ví que essa abordagem tanto filosófica como técnica. É praticamente "Chora agora, ri depois", mas sem a parte de chorar. Pq com o tempo as coisas ficam mais claras... Alguns pontos:

* O erro não é para ser evitado. Logo, 
* Entenda o que você quer do sistema e deixe o erro te guiar até ter o que espera;
* Teste o comportamento esparado e não cada elemeto do sistema 

Sem mais delongas:

#### O que testar?

Vamos usar o arquivo `tests.py` e  criar nossos testes lá.
Ao abrir vocês vão ver que já está o comando importando o `TestCase`.

> Mas o que vamos testar?

Como o objetivo do projeto é criar um sistema qualquer com dados geográficos, vou me ater em testar a inserção de dados, entendendo, com isso, que o meu `model` está coerente com o que eu desejo.  

Para ambos os casos, vou criar objeto do meu modelo `Fenomeno`, no `setUp`, para não ter que criá-lo sempre que for fazer um teste simulando a interação com a base de dados. E nessa carga de dados geográficos, fica claro a estrutura dos dados `geojson`: um dicionário com a chave `type` e `coordinates`, sendo a primeira responsável por identificar o tipo do dado e a última, uma lista de dois valores numéricos.

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

```

:warning: Reparem que: 
1. Para realizar o teste eu preciso importar o models da app em questão;
1. No `test_create()` eu testo se existem objetos inseridos no model `Fenomeno`. Logo, testo se o dado criado no `setUP` foi corretamente incorporado no banco de dados.

Esse último ponto é interessante pois, ao inserir o dado da forma como está sendo feita (usando o método `create()` - e aconteceria o mesmo se estivesse usando o `save()`), sem usar um formulário do django, apenas será validado se o elemento a ser inserido é condizente com o tipo de coluna no banco de dados. Ou seja, o campo `geom` será salvo com sucesso sempre que seja passado um valor em `json`, mesmo que não necessariamente um `geojson`. 

Esse fato é importante para reforçar o entendimento de que o `djgeojson` implementa classes de alto nível a serem trabalhados em `views` e `forms`. No banco, mesmo, temos um campo de `json`. E isso é que o faz simples. Não é preciso ter todo o "aparato" GIS instalado no seu servidor para poder usá-lo.

#### Registrando modelo no admin

Para facilitar, vou usar o django-admin. Trata-se de uma aplicação já criada onde basta registrar os modelos e views que estamos trabalhando para termos uma interface "frontend" genérica.

```python
#admin.py
from django.contrib import admin
from mapProj.core.models import Fenomeno

admin.site.register(Fenomeno)

```
