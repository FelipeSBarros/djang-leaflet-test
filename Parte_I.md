# Criando um sistema Geo super simples com Django

Por super simples, entende-se: 
* Um sistema sem a necessidade da instalação e configuração de base de dados PostgreSQL/GIS, Geoserver, etc;
* Um sistema clásico tipo *Create*, *Update*, *Delete* (CRUD) para dados geográficos;
* Um sistema que não demande operações e consultas espaciais;

### Visão geral da proposta:
Vamos criar um ambiente virtual python e instalar a framework django, para criar o sistema, assim como alguns módulos como `jsonfield`, que nos vai habilitar a criação de campos `json` em nossa base de dados, assim como `django-geojson`. Este ultimo, que depende do `jsonfield`, cria uma instância de dados geográficos, baseando-se e json. Usarei também o módulo [`geojson`](https://pypi.org/project/geojson/), que possui todas as regras *básicas* de validação de dados geográficos, usando a estrutura [`geojson`](https://geojson.org/).

O uso desses três módulos nos permitirá o desenvolvimento de um sistema de gestão de dados geográficos sem a necessidade de termos instalado um sistema de gerenciamento de dados geográficos, como o PostGIS. Sim, nosso sistema será bem limitado a algumas tarefas. Mas en contrapartida, poderemos desenvolvê-lo e implementar soluções "corriqueiras" de forma facilitada. 

No presente exemplo estarei usando [SQSLite](https://www.sqlite.org/index.html), como base de dados.

Nosso projeto se chamará de mapProj. E nele vou criar uma app, dentro da pasta do meu projeto `django`, chamada `core`. Essa organização e nomenclartura usada, vem das sugestões do [Henrique Bastos](https://henriquebastos.net/desmistificando-o-conceito-de-django-apps/). Afinal, o sistema está nascendo. Ainda que eu tenha uma ideia do que ele será, é interessante iniciar com uma app "genérica" e a partir do momento que o sistema se torne complexo, poderemos desacoplá-lo em diferentes apps.

### Criando ambiente de desenvolvimento, projeto e nossa app:

```python
python -m venv .djleaflet # cria ambiente virtual python

# ativando o ambiente virtual:
pip install --upgrade pip

# intalando os módulos a serem usados
pip install django jsonfield django-geojson geojson

# criando projeto
django-admin startproject mapProj .

# criando app dentro do projeto
cd mapProj
manage startapp core

# criando a base de dados incial
manage migrate 

# criando superusuário
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

Perceba que para pode acessar as classes de alto nível criadas pelo pacote `djgeojson`, teremos que adicioná-lo ao `INSTALLED_APPS` do `settings.py`.

### Criando a base de dados

Ainda que eu concorde com o Henrique Bastos, de que a visão de começar os projetos django pelo `models.py` é um tanto "perigosa", por colocar ênfase em uma parte da app e, em muitos casos, negligenciar vários outros atributos e ferramentas que o django nos oferece, irei negligenciar sua abordagem. Afinal, o objetivo deste artigo não é ~~explorar todo o potencial do django, mas sim apresentar uma solução simples no desenvolvimento e implementação de um sistema de gestão de dados geográficos~~ servir como ferramenta de estudo e projeto prático.

Em `models.py` usaremos instâncias de alto nível que o django nos brinda para criar e configurar os campos e as tabelas que teremos em nosso sistema, bem como alguns comportamentos do sistema.

Como estou desenvolvendo um sistema multi propósito, vou tentar mantê-lo bem genérico. A ideia é que vocês possam imaginar o que adequar para um sistema especialista na sua área de interesse. Vou criar, então, uma tabela para mapear "fenômenos" (quaisquer). Eses terão os campos "nome", "data", "hora", latitude, longitude e uma geometria, na qual vou usar `PointField`.

> All geometry types are supported and respectively validated : GeometryField, PointField, MultiPointField, LineStringField, MultiLineStringField, PolygonField, MultiPolygonField, GeometryCollectionField.

```python
# models.py
from django.db import models
from djgeojson.fields import PointField


class Fenomenos(models.Model):
    name = models.CharField(max_length=100,
                            verbose_name='Fenomeno mapeado')
    data = models.DateField(verbose_name='Data da observação')
    hora = models.TimeField()
    longitude = models.FloatField()
    latitude = models.FloatField()
    geom = PointField(blank=True)

    def __str__(self):
        return self.name

```

Percebam que eu importo de `djgeojson` a classe `PointField`. O que o `django-geojson` fez foi criar uma classe [com estrutura de dados goegráfico] de alto nível, mas que no banco de dados será armazenado em um campo json.

Ao fazer isso, poderemos trabalhar com esse dado como se fosse um dado geográfico, com métodos e um sistema básico de validação desse campo (Voltaremos a esse ponto mais à frente). Contudo, nem tudo são flores: **Consultas e operações espaciais não são contemplados**. Para tais casos, voçê precisará do PstGIS.
Mais informações sobre o [`djgeojson`](https://pypi.org/project/django-geojson/)

Pronto, já temos o modelo da 'tabela de dados "geográficos"'. Lembrando que não temos todo o poder de uma base de dados, mas sim, uma construção em json para minimamente armazenar y validar dados geográficos.

Contudo, esse modelo ainda não foi "commitado"/"registrado" para/na a nossa base. Para isso:

```python
manage makemigrations
manage migrate
```

O `makemigrations` analisa o `models.py` e o compara com a versão anterior identificando as alterações e criando um arquivo que será executado pelo `migrate`, aplicando tais alterações ao banco de dados. Aprendi com o Henrique Bastos e [@Cuducos](twitter.com/cuducos) que o migrate é um sistema de versionamento da estrutura do banco de dados, permitindo retroceder, quando necessário, à outras versões. 

### Criando o formulário

Como a ideia é abusar das "pilhas já incluídas" no django, vou usar o `ModelForm` para criar o formulário para o carregamento de dados. O `ModelForm` facilita esse processo (talvez haja outro que simplifique ainda mais) criando um formulário a partir da estrutura dos dados do `model`.

Aliás, é importante pensar que os formulários do django vão muito além da "carga de dados", já que são os responsáveis por cuidar da interação com o usuário e o(s) processo(s) de validação e limpeza dos dados preenchidos.

Digo isso, pois ao meu `FenomenosForm`, eu sobreescrevo o método `clean()`, que cuida da validação e limpeza do formulário e incluo nele:
1. a construção dos dados do campo `geom` a partir dos valores dos campos de `latitude` e `longitude`;
1. a validação do campo geom;

```python
# forms.py
from django.core.exceptions import ValidationError
from django.forms import ModelForm, HiddenInput
from mapProj.core.models import Fenomenos
from geojson import Point


class FenomenosForm(ModelForm):
    class Meta:
        model = Fenomenos
        fields = '__all__'
        widgets = {
            'geom': HiddenInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        lon = cleaned_data.get('longitude')
        lat = cleaned_data.get('latitude')
        cleaned_data['geom'] = Point((lon, lat))
        if not cleaned_data['geom'].is_valid:
            raise ValidationError('Geometria com erro')
        return cleaned_data

```

Ainda que pareça simples, não foi fácil chegar a esse processo de validação do campo `geom`. O [Cuducos](twitter.com/cuducos) me ajudou muito. De forma resumida, percebi que o `djgeojson` apenas valida o tipo de geometria do campo e não a sua consistência. Aos conversar com os desenvolvedores, me disseram que toda a lógica de validação de objetos `geojson` estavam sendo centralizados no módulo homônimo. 

Por isso eu carrego a classe `Point` do módulo `geojson` e designo o campo `geom` como instância dessa classe. Assim, passo a poder contar com um processo de validação mais consistente.

Obs.: Como não espero que o usuário carregue no formulário o json do campo `geom`, e como não posso excluí-lo do mesmo, já que ele será construído no processo de limpeza, usei o `HiddenInput()` `widget` para escondê-lo.

#### Mas ~~antes,~~ [e o] teste ~~!~~ ?

Pois é, eu adoraria apresentar isso usando a abordagem *Test Driven Development (TDD)*. Mas, talvez pela falta de prática, conhecimento e etc, vou apenas apontar onde e como eu testaria esse sistema. Faço isso como uma forma de estudo, mesmo. Também me pareceu complicado apresentar a abordagem TDD em um artigo, já que a mesma se faz de forma incremental.

##### Sobre TDD

Com o Henrique Bastos e toda a comunidade do [*Welcome to The Django*](https://medium.com/welcome-to-the-django/o-wttd-%C3%A9-tudo-que-eu-ensinaria-sobre-prop%C3%B3sito-de-vida-para-mim-mesmo-se-pudesse-voltar-no-tempo-d73e516f911c) ví que essa abordagem é tanto filosófica quanto técnica. É praticamente "Chora agora, ri depois", mas sem a parte de chorar. Pois com o tempo as coisas ficam mais claras... Alguns pontos:

* O erro não é para ser evitado no processo de desenvolvimento, mas sim quando estive em produção. Logo, 
* Entenda o que você quer do sistema, crie um teste antes de implementar e deixe o erro te guiar até ter o que deseja;
* Teste o comportamento esparado e não cada elemeto do sistema; 

Sem mais delongas:

#### O que testar?

Vamos usar o arquivo `tests.py` e  criar nossos testes lá.
Ao abrir vocês vão ver que já está o comando importando o `TestCase`.

> Mas o que vamos testar?

Como pretendo testar tanto a estrutura da minha base de dados, quanto o formulário e, de quebra, a validez do meu campo `geom`, faço o import do modelo `Fenomenos` e do form `FenomenosForm`.

O primeiro teste será a carga de dados. Então, vou instanciar um objeto com o resultado da criação de um elemento do meu `model` `Fenomeno`. Faço isso no `setUp`, para não ter que criá-lo sempre que for fazer um teste relacionado à carga de dados.

O teste seguinte será relacionado ao formulário e por isso instancio um formulário com os dados carregados e testo a sua validez. Ao fazer isso o formulário passa pelo processo de limpeza, onde está a construção e validação do campo `geom`. Se qualquer campo for preenchido com dados errados ou inadequados, o django retornará `False` ao método `is_valid()`. Ou seja, se eu tiver construido o campo `geom` de forma equivocada, passando mais ou menos parâmetros que o esperado o nosso teste irá avisar, avitando surpresas.

```python
# tests.py
from django.test import TestCase
from mapProj.core.models import Fenomenos
from mapProj.core.forms import FenomenosForm


class ModelGeomTest(TestCase):
    def setUp(self):
        self.fenomeno = Fenomenos.objects.create(
            name='Arvore',
            data='2020-11-06',
            hora='09:30:00',
            longitude = 22.0,
            latitude = 22.0
        )

    def test_create(self):
        self.assertTrue(Fenomenos.objects.exists())


class FenomenosFormTest(TestCase):
    def setUp(self):
        self.form = FenomenosForm({
            'name': 'Teste',
            'data': '2020-01-01',
            'hora': '09:12:12',
            'longitude': -45,
            'latitude': -22})

    def test_form_is_valid(self):
        """"geom Point must be valid"""
        validation = self.form.is_valid()
        self.assertTrue(validation)
```

:warning: Reparem que:
1. No `test_create()` eu testo se existem objetos inseridos no model `Fenomeno`. Logo, testo se o dado criado no `setUP` foi corretamente incorporado no banco de dados.
1. No `test_form_is_valid()` estou testando tanto, se os dados carregados são condizentes com o informado no model, quanto a validez do campo `geom`.

A diferença entre ambos está no fato de ao inserir os dados usando o método `create()` - e aconteceria o mesmo se estivesse usando o `save()` -, apenas será validado se o elemento a ser inserido é condizente com o tipo de coluna no banco de dados. Afinal, não estou instanciando o formulário. Dessa forma, eu não estou validando a consistência do campo `geom`, já que o mesmo, caso seja informado, será salvo com sucesso sempre que represente um `json`. 

Esse fato é importante para reforçar o entendimento de que o `djgeojson` implementa classes de alto nível a serem trabalhados em `views` e `models`. No banco, mesmo, temos um campo de `json`.
Enquanto que, para poder validar a consistência do campo `geom`, preciso passar os dados pelo formulário onde, no processo de limpeza do mesmo, o campo será criado e validado usando o módulo `geojson`. 

### Registrando modelo no admin

Para facilitar, vou usar o django-admin. Trata-se de uma aplicação já criada onde basta registrar os modelos e views que estamos trabalhando para termos uma interface "frontend" genérica.

```python
#admin.py
from django.contrib import admin
from mapProj.core.models import Fenomenos
from mapProj.core.forms import FenomenosForm

class FenomenoAdmin(admin.ModelAdmin):
    model = Fenomenos
    form = FenomenosForm

admin.site.register(Fenomenos, FenomenoAdmin)
```

### To be continued...
Até o momento já temos algo bastante interessante: um sistema de CRUD que nos permite adicionar, editar e remover dados geográficos. Talvez você esteja pensando consigo mesmo: 
> "OK. Mas o que foi feito até agora, poderia ter sido feito basicamente com uma base de dados que possuam as colunas latitude e longitude".

Eu diria que sim, até certo ponto. Um grande diferencia, eu diria da forma como foi iplementada é o uso das ferramentas de validação dos dados com o módulo `geojson`.

A ideia é, a seguir (e seja lá quando isso for), extender a funcionalidade do sistema ao implementar um webmap para visualizar os dados mapeados.
