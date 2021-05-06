# Criando um sistema para gestão de dados geográficos de forma simples e robusta

Por simples, entende-se: 
* Um sistema sem a necessidade da instalação e configuração de base de dados PostgreSQL/GIS, Geoserver, etc;
* Um sistema clássico tipo *Create*, *Retrieve*, *Update*, *Delete* (CRUD) para dados geográficos;
* Um sistema que não demande operações e consultas espaciais, mas que garanta a qualidade dos dados geográficos;

### Visão geral da proposta:
Vamos criar um ambiente virtual Python e instalar a framework Django, para criar o sistema, assim como alguns módulos como [`jsonfield`](https://pypi.org/project/jsonfield/), que nos vai habilitar a criação de campos `JSON` em nossa base de dados; [`django-geojson`](https://pypi.org/project/django-geojson/), que depende do `jsonfield` e será responsável por habilitar instâncias de dados geográficos, baseando-se em `JSON`; [`geojson`](https://pypi.org/project/geojson/), que possui todas as regras *básicas* de validação de dados geográficos, usando a estrutura homônima, [`geojson`](https://geojson.org/).

O uso desses três módulos nos permitirá o desenvolvimento de um sistema de gestão de dados geográficos sem a necessidade de termos instalado um sistema de gerenciamento de dados geográficos, como o PostGIS. Sim, nosso sistema será bem limitado a algumas tarefas. Mas em contrapartida, poderemos desenvolvê-lo e implementar soluções "corriqueiras" de forma facilitada. 

No presente exemplo estarei usando [SQLite](https://www.sqlite.org/index.html), como base de dados.

Nosso projeto se chamará de *map_proj*. E nele vou criar uma app, dentro da pasta do meu projeto `Django`, chamada `core`. Essa organização e nomenclatura usada, vem das sugestões do [Henrique Bastos](https://github.com/okfn-brasil/jarbas/issues/28#issuecomment-256117262). Afinal, o sistema está nascendo. Ainda que eu tenha uma ideia do que ele será, é interessante iniciar com uma aplicação "genérica" e a partir do momento que o sistema se torne complexo, poderemos desacoplá-la em diferentes aplicações.

### Criando ambiente de desenvolvimento, projeto e nossa app:

```python
python -m venv .djleaflet # cria ambiente virtual python
# ativando o ambiente virtual:
source ./venv/bin/activate

# atualizando o pip
pip install --upgrade pip

# intalando os módulos a serem usados
pip install django jsonfield django-geojson geojson

# criando projeto
django-admin startproject map_proj .

# criando app dentro do projeto
cd map_proj
python manage.py startapp core

# criando a base de dados inicial
python manage.py migrate 

# criando superusuário
python manage.py createsuperuser 
```

#### Adicionando os módulos e a app ao projeto

Agora é adicionar ao `map_proj/settings.py`, a app criada e os módulos que usaremos.

```python
# setting.py
INSTALLED_APPS = [
    ...
    'djgeojson',
    'map_proj.core',
]
```

Perceba que para poder acessar as classes de alto nível criadas pelo pacote `djgeojson`, teremos que adicioná-lo ao `INSTALLED_APPS` do `settings.py`.

### Criando a base de dados

Ainda que eu concorde com o Henrique Bastos, que a visão de começar os projetos Django pelo `models.py` é um tanto "perigosa", por colocar ênfase em uma parte da app e, em muitos casos, negligenciar vários outros atributos e ferramentas que o Django nos oferece, irei desconsiderar sua abordagem. Afinal, o objetivo deste artigo não é explorar todo o potencial do Django, mas sim apresentar uma solução simples no desenvolvimento e implementação de um sistema de gestão de dados geográficos para servir como ferramenta de estudo e projeto prático.

Em `models.py` usaremos instâncias de alto nível que o Django nos brinda para criar e configurar os campos e as tabelas que teremos em nosso sistema, bem como alguns comportamentos do sistema.

Como estou desenvolvendo um sistema multi propósito, vou tentar mantê-lo bem genérico. A ideia é que vocês possam imaginar o que adequar para um sistema especialista na sua área de interesse. Vou criar, então, uma tabela para mapear "fenômenos" (quaisquer). Esse modelo terá os campos *nome*, *data*, *hora* e *geometria*, a qual será uma instância de `PointField`.

O `PointField` é uma classe criada pelo `djgeojson` que nos permite usar um campo para dados geográficos sem ter toda a infraestrutura do PostGIS, instalada, por exemplo. Nesse caso, estou simulando um campo de ponto, mas, de acordo com a documentação do pacote, todas as geometrias usadas em dados espaciais são suportadas: 

> All geometry types are supported and respectively validated : GeometryField, PointField, MultiPointField, LineStringField, MultiLineStringField, PolygonField, MultiPolygonField, GeometryCollectionField. ( [`djgeojson`](https://django-geojson.readthedocs.io/en/latest/models.html) )

```python
# models.py
from django.db import models
from djgeojson.fields import PointField


class Fenomeno(models.Model):
    nome = models.CharField(max_length=100,
                            verbose_name='Fenomeno mapeado')
    data = models.DateField(verbose_name='Data da observação')
    hora = models.TimeField()
    geom = PointField(blank=True)

    def __str__(self):
        return self.nome

```

Percebam que eu importo de `djgeojson` a classe `PointField`. O que o `django-geojson` fez foi criar uma classe [com estrutura de dados geográfico] de alto nível, mas que no banco de dados será armazenado em um campo `JSON`. Vale a pena deixar claro: não espero que o usuário do meu sistema saiba preencher o campo `geom` em formato `JSON`. Por isso, criarei no `forms.py`, os campos *latitude* e *longitude* e a partir deles, o campo geom será preenchido. Detalharei esse processo mais adiante. 

Pronto, já temos o modelo da 'tabela de dados "geográficos"', mas esse modelo ainda não foi registrado em nossa base. Para isso:

```python
python manage.py makemigrations
python manage.py migrate
```

O `makemigrations` analisa o `models.py` e o compara com a versão anterior identificando as alterações e criando um arquivo que será executado pelo `migrate`, aplicando tais alterações ao banco de dados. Aprendi com o Henrique Bastos e [Cuducos](https://twitter.com/cuducos) que o migrate é um sistema de versionamento da estrutura do banco de dados, permitindo retroceder, quando necessário, a outras versões. 

### Criando o formulário

Vou aproveitar algumas "pilhas já incluídas" do Django, ao usar o `ModelForm` para criar o formulário para o carregamento de dados. O `ModelForm` facilita esse processo.

Aliás, é importante pensar que os formulários do Django vão muito além da "carga de dados", já que são os responsáveis por cuidar da interação com o usuário e o(s) processo(s) de validação e limpeza dos dados preenchidos.

Digo isso, pois ao meu `FenomenosForm`, eu sobreescrevo o método `clean()`, que cuida da validação e limpeza do formulário e incluo nele:
1. a construção dos dados do campo `geom` a partir dos valores dos campos de *latitude* e *longitude* (criados exclusivamente para a gerção do campo geom);
1. a validação do campo geom;

```python
# forms.py
from django.core.exceptions import ValidationError
from django.forms import ModelForm, FloatField
from map_proj.core.models import Fenomeno
from geojson import Point


class FenomenoForm(ModelForm):
    longitude = FloatField()
    latitude = FloatField()
    class Meta:
        model = Fenomeno
        fields = ('nome', 'data', 'hora', 'latitude', 'longitude')

    def clean(self):
        cleaned_data = super().clean()
        lon = cleaned_data.get('longitude')
        lat = cleaned_data.get('latitude')
        cleaned_data['geom'] = Point((lon, lat))

        if not cleaned_data['geom'].is_valid:
            raise ValidationError('Geometria inválida')
        return cleaned_data

```

Ainda que pareça simples, não foi fácil chegar a essa estratégia de estruturação dos `models` e `forms`. Contei com a ajuda e paciencia do [Cuducos](https://twitter.com/cuducos). Inicialmente eu mantinha latitude e longitude no meu `models`. Mas fazendo assim, além de ter uma redundância de dados e uma abertura a erros potenciais, estaria armazenando dados que não devo usar depois de contruir o campo geom. Uma alternativa, discutida com o Cuducos foi de ter tanto *latitude* como *longitude* no `models`, mas o atributo `geom` como [propriedade](https://docs.python.org/3/howto/descriptor.html#properties). Ainda que seja uma estratégia consistente, a redundância se mantém.

O processo de validação do campo `geom` também foi fruto de muita discussão. De forma resumida, percebi que o `djgeojson` apenas valida o tipo de geometria do campo e não a sua consistência. Ao conversar com os desenvolvedores, me disseram que toda a lógica de validação de objetos `geojson` estavam sendo centralizados no módulo homônimo.

Por isso eu carrego a classe `Point` do módulo `geojson` e designo o campo `geom` como instância dessa classe. Assim, passo a poder contar com um processo de validação mais consistente, como o método `is_valid`, usado anteriormente.

#### Mas e o teste?

Pois é, eu adoraria apresentar isso usando a abordagem *Test Driven Development (TDD)*. Mas, talvez pela falta de prática, conhecimento e etc, vou apenas apontar onde e como eu testaria esse sistema. Faço isso como uma forma de estudo, mesmo. Também me pareceu complicado apresentar a abordagem TDD em um artigo, já que a mesma se faz de forma incremental.

##### Sobre TDD

Com o Henrique Bastos e toda a comunidade do [*Welcome to The Django*](https://medium.com/welcome-to-the-django/o-wttd-%C3%A9-tudo-que-eu-ensinaria-sobre-prop%C3%B3sito-de-vida-para-mim-mesmo-se-pudesse-voltar-no-tempo-d73e516f911c) vi que essa abordagem é tanto filosófica quanto técnica. É praticamente "Chora agora, ri depois", mas sem a parte de chorar. Pois com o tempo as coisas ficam mais claras... Alguns pontos:

* O erro não é para ser evitado no processo de desenvolvimento, mas sim quando estive em produção. Logo, 
* Entenda o que você quer do sistema, crie um teste antes de implementar e deixe o erro te guiar até ter o que deseja;
* Teste o comportamento esperado e não cada elemento do sistema; 

Sem mais delongas:

##### O que testar?

Vamos usar o arquivo `tests.py` e  criar nossos testes lá.
Ao abrir vocês vão ver que já está o comando importando o `TestCase`.

> Mas o que vamos testar?

Como pretendo testar tanto a estrutura da minha base de dados, quanto o formulário e, de quebra, a validação do meu campo `geom`, faço o `import` do modelo `Fenomenos` e do form `FenomenosForm`.

:warning: Essa não é uma boa prática. O ideal é criar uma pasta para os testes e separá-los em arquivos distintos. Um para cada elemento do sistema (model, form, view, etc).

O primeiro teste será a carga de dados. Então, vou instanciar um objeto com o resultado da criação de um elemento do meu `model` `Fenomeno`. Faço isso no `setUp`, para não ter que criá-lo sempre que for fazer um teste relacionado à carga de dados.

O teste seguinte será relacionado ao formulário e por isso instancio um formulário com os dados carregados e testo a sua validez. Ao fazer isso o formulário passa pelo processo de limpeza, onde está a construção e validação do campo `geom`. Se qualquer campo for preenchido com dados errados ou inadequados, o django retornará `False` ao método `is_valid`. Ou seja, se eu tiver construido o campo `geom` de forma equivocada, passando mais ou menos parâmetros que o esperado o nosso teste irá avisar, evitando surpresas.

```python
# tests.py
from django.test import TestCase
from geojson import Point

from map_proj.core.models import Fenomeno
from map_proj.core.forms import FenomenoForm


class ModelGeomTest(TestCase):
    def setUp(self):
        self.fenomeno = Fenomeno.objects.create(
            nome='Arvore',
            data='2020-11-06',
            hora='09:30:00'
        )

    def test_create(self):
        self.assertTrue(Fenomeno.objects.exists())


class FenomenoFormTest(TestCase):
    def setUp(self):
        self.form = FenomenoForm({
            'nome': 'Teste',
            'data': '2020-01-01',
            'hora': '09:12:12',
            'longitude': -45,
            'latitude': -22})
        self.validation = self.form.is_valid()

    def test_form_is_valid(self):
        """"form must be valid"""
        self.assertTrue(self.validation)

    def test_geom_coordinates(self):
        """after validating, geom have same values of longitude and latitude"""
        self.assertEqual(self.form.cleaned_data['geom'], Point(
            (self.form.cleaned_data['longitude'],
        self.form.cleaned_data['latitude'])))

    def test_geom_is_valid(self):
        """geom must be valid"""
        self.assertTrue(self.form.cleaned_data['geom'].is_valid)

```

:warning: Reparem que:
1. No `test_create()` eu testo se existem objetos inseridos no model `Fenomeno`. Logo, testo se o dado criado no `setUp` foi corretamente incorporado no banco de dados.
1. Na classe `FenomenosFormTest` eu crio uma instância do meu modelForm e realizo três testes:
   * `test_form_is_valid()` estou testando se os dados carregados são condizentes com o informado no model e, pelo fato desse método usar o método `clean()`, posso dizer que estou testando indiretamente a validez do campo `geom`. Caso ele não fosse válido, o form também não seria válido.
   * Em `test_geom_coordinates()` testo se após a validação o campo geom foi criado como esperado (como uma instância de Point com os dalores de longitude e latitude).
   * O teste `test_geom_is_valid()` serve para garantir que a contrução do campo geom é valido. Ainda que ao testar se o formulário é valido eu estaria implicitamente testando a validez do campo geom, esse teste serve para garantir a criação válida do campo. Afinal, por algum motivo (como por exemplo, refatoração), pode ser que façamos alguma alteração no método `clean()` que mantenha o formulário como válido mas deixe de garantir a validez do campo geom.

A diferença entre as classes de teste criadas está no fato de ao inserir os dados usando o método `create()` - e aconteceria o mesmo se estivesse usando o `save()` -, apenas será validado se o elemento a ser inserido é condizente com o tipo de coluna no banco de dados. Vale deixar claro: Dessa forma, eu não estou validando a consistência do campo `geom`, já que o mesmo, caso seja informado, será salvo com sucesso sempre que represente um `JSON`. 

Esse fato é importante para reforçar o entendimento de que o `djgeojson` implementa classes de alto nível a serem trabalhados em `views` e `models`. No banco, mesmo, temos um campo de `JSON`.
Enquanto que, para poder validar a consistência do campo `geom`, preciso passar os dados pelo formulário onde, no processo de limpeza do mesmo, o campo será criado e validado usando o módulo `geojson`. Por isso a classe com os testes relacionados ao comportamento do formulário.

### Registrando modelo no admin

Para facilitar, vou usar o django-admin. Trata-se de uma aplicação já criada onde basta registrar os modelos e views que estamos trabalhando para termos uma interface "frontend" genérica.

```python
#admin.py
from django.contrib import admin
from map_proj.core.models import Fenomeno
from map_proj.core.forms import FenomenoForm

class FenomenoAdmin(admin.ModelAdmin):
    model = Fenomeno
    form = FenomenoForm

admin.site.register(Fenomeno, FenomenoAdmin)

```

### To be continued...
Até o momento já temos algo bastante interessante: um sistema de CRUD que nos permite adicionar, editar e remover dados geográficos. Talvez você esteja pensando consigo mesmo: 

> "OK. Mas o que foi feito até agora, poderia ter sido feito basicamente com uma base de dados que possuam as colunas latitude e longitude".

Eu diria que sim, até certo ponto. Uma grande diferença, eu diria, da forma como foi implementada é o uso das ferramentas de validação dos dados com o módulo `geojson`.

A ideia é, a seguir (e seja lá quando isso for), extender a funcionalidade do sistema ao implementar um webmap para visualizar os dados mapeados.
