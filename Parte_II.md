# Criando um sistema para gestão de dados geográficos de forma simples e robusta II

Na [primeira publicação](https://www.linkedin.com/pulse/criando-um-sistema-para-gest%C3%A3o-de-dados-geogr%C3%A1ficos-e-felipe-/) onde exploro a possibilidade de implementar um sistema de gestão de dados geoespaciais com Django, sem a necessidade de usar um servidor com PostGIS, vimos sobre:
* o [`django-geojson`](https://django-geojson.readthedocs.io/en/latest/) para simular um campo geográfico no models;
* o [`geojson`](https://geojson.readthedocs.io/en/latest/) para criar um objeto da classe *geojson* e realizar as validações necessárias para garantir robustez do sistema;  
* a criação do fomulário de registro de dados usando o [`ModelForm`](https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/#modelform);  

Agora é hora de evoluir e expandir um pouco o sistema criado. Nessa publicação vamos criar validadores de longitude e latitude para poder restringir a inserção de dados a uma determinada região;  
* adicionar uma propriedade ao modelo que será usada no *popup* do mapa em [`leaflet`](https://leafletjs.com/);
* criar uma view para visualizar os dados em mapas usando `GeoJSONLayerView`, do [`django-geojson`](https://django-geojson.readthedocs.io/en/latest/);
* ~~instalar e usar o [`django-leaflet`](https://django-leaflet.readthedocs.io/en/latest/) para poder usar o `widget` além de outras funcionalidades;~~
* ~~Tudo isso testando se tais funcionalidades ou propriedades estão com o comportamento esperado;~~  
* ~~fazer deploy no [heroku](heroku.com)(?)~~  
    * ~~Um argumento para fazê-lo é levar a implementação até o final.~~  
    * ~~O leaflet depende de funcionalidades do GDAL. E o heroku possui o [heroku-geo-buildpack](https://github.com/heroku/heroku-geo-buildpack) para isso :heart:~~  

Vamos lá!

## criando validadores de longitude e latitude  

### Sobre os validadores:  
Os validadores ([`validators`](https://docs.djangoproject.com/en/3.2/ref/forms/validation/#validators), em inglês) fazem parte do sistema de validação de formulários e de campos do Django. Ao criarmos campos de uma determinada classe no nosso modelo, como por exemplo *integer*, o Django cuidará automaticamente da validação do valor passado a este campo pelo formulário, retornando um erro quando o usuário ingressar um valor de texto no campo em questão, por exemplo. O interessante é que além dos validadores já implementados para cada classe, podemos criar outros, conforme a nossa necessidade.

> Por que necessitamos um validador de `latitude` e `longitude`?

Como estou explorando o desenvolvimento de um sistema de gestão de dados geográficos com recursos limitados, ou seja, sem uma infraestrutura de operações e consultas espaciais, não poderei consultar se o par de coordenadas inserido pelo usuário está contido nos limites de um determinado estado (uma operação clássica com dados geográficos). Não ter essa possibilidade de validação poderá colocar em risco a qualidade do dado inserido.

E como não se abre mão quando a questão é qualidade, uma saída será a criação de validadores personalizados para os campos de `latitude` e `longitude`, garantindo que esses possuem valores condizentes à nossa área de interesse.

**O que precisamos saber:**
os `validators` são funções que recebem um valor, apenas (neste caso, o valor inserido pelo usuário no campo a ser validado), que passará por uma lógica de validação retornando um [`ValidationError`](https://docs.djangoproject.com/en/3.2/ref/forms/validation/#raising-validation-error) quando o valor inserido não passar nos testes. Com o `ValidationError` podemos customizar uma mensagem de erro, indicando ao usuário o motivo do valor não ter sido considerado válido.  

Então, criarei validadores dos campos de `latitude` e `longitude` para sempre que entrarem com valores que não contemplem a área do estado do Rio de Janeiro, um `ValidationError` será retornado.  

> :warning: Essa não é uma solução ótima já que, dessa forma, estamos considerando o *bounding box* do estado em questão, e com isso haverá áreas onde as coordenadas serão válidas, ainda que não estejam internas ao território estadual. Ainda assim, acredito que seja uma solução boa suficiente para alguns casos, principalmente por não depender de toda infraestrutura de GIS.

**O que é um `bouding box`?**

*Bounding box* poderia ser traduzido por "retângulo envolvente" do estado, ou de uma feição espacial. Na imagem abaixo, vemos o território do estado do Rio de Janeiro e o retângulo envolvente que limita as suas coordenadas máximas e mínimas de longitude e latitude.  

![](./map_proj/img/RJ_bbox.png)

Percebam que, como mencionado antes, o que conseguimos garantir é que os pares de coordenadas estejam em alguma área interna ao retângulo em questão o que não garante que as mesmas estejam no território do estado do Rio de Janeiro.

## Criando os testes: [ melhorar paragrafo abaixo ]  

Antes de tudo, criamos os testes.
Para isso, criarei uma função chamada `update_values` que receberá um `**kwargs`, que é uma forma de passar a uma função um conjunto de argumentos nomeados. Nessa função, crio um dicionário tendo como chave os nomes dos campos do meu `ModelForm`, e como valores, os valores esperados e válidos de cada campo.

Logo em seguida, crio um objeto chamado `final_data` que será o dicionário `validForm` criado anteriormente, mas com os parâmetros nomeados passados como `**kwargs` da função. Esse dicionário com os valores atualizados serão usadas para instanciar o meu `ModelForm` que será retornado ao fim da execução.

Fiz isso para poder atualizar, a cada teste, apenas os campos que quero simular valores a serem validados, sem ter que instanciar e passar sempre os valores do `ModelForm`.

```python
# tests.py
class FenomenoFormValidatorsTest(TestCase):
    def update_values(self, **kwargs):
        valid_form = {
            'nome': 'Teste',
            'data': '2020-01-01',
            'hora': '09:12:12',
            'longitude': -42,
            'latitude': -21}

        final_data = valid_form.update(**kwargs)
        form = FenomenoForm(final_data)
        return form
```

Assim, eu posso criar diferentes métodos de *Test Case*, usando o método criando anteriormente alterando o valor inicial a um inválido, a ser testado.

Nos método uso o `assertEqual` para confirmar que o texto da mensagem de erro é o que esperamos. Veja o link a seguir para saber sobre outros [`assertions`](https://docs.python.org/3/library/unittest.html#unittest.TestCase.debug).

```python
# tests.py
def test_max_longitude(self):
  form = self.create_form(longitude='-45')
  form.is_valid()
  self.assertEqual(form.errors["longitude"][0], 'Coordenada longitude fora do contexto do estado do Rio de Janeiro')


def test_min_longitude(self):
  form = self.create_form(longitude='-40')
  form.is_valid()
  self.assertEqual(form.errors["longitude"][0], 'Coordenada longitude fora do contexto do estado do Rio de Janeiro')


def test_max_latitude(self):
  form = self.create_form(latitude='-24')
  form.is_valid()
  self.assertEqual(form.errors["latitude"][0], 'Coordenada latitude fora do contexto do estado do Rio de Janeiro')


def test_min_latitude(self):
  form = self.create_form(latitude='-19')
  form.is_valid()
  self.assertEqual(form.errors["latitude"][0], 'Coordenada latitude fora do contexto do estado do Rio de Janeiro')

```

Fazemos rodar os testes e teremos erros como esses:

```python
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
...E.E..
======================================================================
ERROR: test_max_latitude (map_proj.core.tests.FenomenoFormValidatorsTest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/media/felipe/DATA/Repos/Django_Leaflet_Test/map_proj/core/tests.py", line 78, in test_max_latitude
    self.assertEqual(form.errors["latitude"][0], 'Coordenada latitude fora do contexto do estado do Rio de Janeiro')
KeyError: 'latitude'

======================================================================
ERROR: test_min_latitude (map_proj.core.tests.FenomenoFormValidatorsTest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/media/felipe/DATA/Repos/Django_Leaflet_Test/map_proj/core/tests.py", line 83, in test_min_latitude
    self.assertEqual(form.errors["latitude"][0], 'Coordenada latitude fora do contexto do estado do Rio de Janeiro')
KeyError: 'latitude'

----------------------------------------------------------------------
Ran 8 tests in 0.012s

FAILED (errors=2)
Destroying test database for alias 'default'...

```  

Ou seja, o `forms` após ser validado deveria conter um atributo *errors* tendo como chave o nome do campo que apresentou dados inválidos. Como não temos os validadores criados, ainda, os campos `latitude` não foi encontrado pelo teste executado.

## Criando e usando validadores:

Para superá-los criamos, enfim, os validadores em um arquivo `validators.py`:

```python
# validators.py
from django.core.exceptions import ValidationError


def validate_longitude(lon):
    if lon < -44.887212 or lon > -40.95975:
        raise ValidationError("Coordenada longitude fora do contexto do estado do Rio de Janeiro", "erro longitude")


def validate_latitude(lat):
    if lat < -23.366868 or lat > -20.764962:
        raise ValidationError("Coordenada latitude fora do contexto do estado do Rio de Janeiro", "erro latitude")
```

Com esses validadores estou garantindo que ambos latitude e longitude estejam na área de interesse e, caso contrário, retorno um erro informando ao usuário.

E é preciso adicioná-los ao `forms.py` para que sejam usados:

```python
# forms.py
from map_proj.core.validators import validate_longitude, validate_latitude

class FenomenoForm(ModelForm):
    longitude = FloatField(validators=[validate_longitude])
    latitude = FloatField(validators=[validate_latitude])
...
```

No desenvolvimento dessa solução percebi pelos testes criados que, ao informar uma latitude ou longitude que não passe pela validação, a criação do campo `geom` se tornava inválido por não receber um desses valores, gerando dois erros: o de validação do campo e o de validação do campo `geom`. Lembre-se que é no método `clean` do formulário que o campo `geom` recebe os valores de `longitude` e `latitude` formando uma classe `geojson` para, logo em seguida ser validado.

Para evitar isso, alterei o método clean de forma garantir que o campo `geom` só seja criado e validado, quando ambos valores (`longitude` e `latitude`) existirem. Ou seja, tenham passado pelos validadores sem erro.

```python
#forms.py
    def clean(self):
        cleaned_data = super().clean()
        lon = cleaned_data.get('longitude')
        lat = cleaned_data.get('latitude')
        if not all((lon, lat)):
            raise ValidationError('Erro em latitude ou longitude')
        
        cleaned_data['geom'] = Point((lon, lat))
        if not cleaned_data['geom'].is_valid:
                raise ValidationError('Geometria inválida')
        
        return cleaned_data

```

> Outro ponto (na verdade, erro) importante que só percebi a partir dos testes é que no `forms.py` eu não estava considerando o campo `geom` na lista de `fields` a serem usados. Com isso o mesmo não é passado ao banco de dados, mesma passando pelo método `clean` que o cria.

Por esse motivo, tive que alterar algumas coisas no `forms.py`:
- Inseri o campo `geom` à tupla de `fields` do `forms.py`. 
- Inseri o campo `geom` com um widget de `HiddenInput`. Esse último, o fiz por se tratar de um campo que não quero expor ao usuário, já que será criado automaticamente no método `clean`. 

Finalmente, a classe `Meta` do `forms.py` ficou da seguinte forma:

```python
    class Meta:
        model = Fenomeno
        fields = ('nome', 'data', 'hora', 'latitude', 'longitude', 'geom')
        widgets = {'geom': HiddenInput()}
```

## View GeoJSONLayerView

A serialização ou, em inglês `serialization`, é o processo/mecanismo de tradução dos objetos armazenados na base de dados em outros formatos, em geral baseado em texto (por exemplo, XML ou JSON), para serem enviados ou consumidos no processo de `request/response`. 

No nosso caso isso será importante pois para apresentar os dados armazenados pelo projeto em um *webmap*, precisaremos servi-los no formato `geojson`. Mas não precisaremos nos preocupar com praticamente nada disso pois o `django-geojson` cuida de tudo ao oferecer-nos a classe [`GeoJSONLayerView`](https://django-geojson.readthedocs.io/en/latest/views.html#geojson-layer-view), que é um [`mixin`](https://docs.djangoproject.com/en/3.2/topics/class-based-views/mixins/) que, em base ao modelo informado do nosso projeto, serializa os dados em `geojson` usando a classe `GeoJSONSerializer` e os serve em uma `view`. É bastante coisa para apenas algumas linhas de código.

Para entender a serialização, veja o exemplo abaixo. Ao acessar os dados do banco de dados, temos uma `QuerySet`. Ao acessar a geometria de um objeto do banco de dados, temos um `geojson`. Ao serializá-lo com o `GeoJSONSerializer`, temos como retorno uma [`FeatureCollection`](https://datatracker.ietf.org/doc/html/rfc7946#section-3.3) já em formato `geojson`, tendo como propriedades os campos do `model`:

```python
>>> Fenomeno.objects.all()
<QuerySet [<Fenomeno: fenomeno_teste>]>

>>> Fenomeno.objects.get(pk=3).geom
{'type': 'Point', 'coordinates': [-42.0, -22.0]}

>>> from djgeojson.serializers import Serializer as GeoJSONSerializer
>>> GeoJSONSerializer().serialize(Fenomeno.objects.all(), use_natural_keys=True, with_modelname=False)
'{"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {"nome": "teste", "data": "2021-06-22", "hora": "02:07:57"}, "id": 3, "geometry": {"type": "Point", "coordinates": [-42.0, -22.0]}}], "crs": {"type": "link", "properties": {"href": "http://spatialreference.org/ref/epsg/4326/", "type": "proj4"}}}'
```

Mais sobre serialização pode ser encontrado [aqui](https://django-portuguese.readthedocs.io/en/1.0/topics/serialization.html) ou [aqui, com outro exemplo relacionado a dado geográfico usando o GeoDjango](https://docs.djangoproject.com/en/3.2/ref/contrib/gis/serializers/).

Então, ciente de toda a mágica por trás do `GeoJSONLayerView` e o seu resultado, vamos criar os testes para essa `view`.

### Criando os testes da `View`

Como estou testando justamente uma `view` que serializa o objeto do meu modelo em formado `geojson` e, sabendo que o `geom` só é criado ao usarmos o `ModelForm`, no `tests.py` vou uma instância do `ModelForm`, em uma nova classe de `TestCase`. Essa instância com valores válidos são, em seguida, salvo no banco de dados (do teste).

Primeiro testo se o *status code* do request (método "get") ao *path* que pretendo usar para essa views (no caso, "/geojson/"), retorna 200, código que indica sucesso. [Veja mais sobre os códigos aqui](https://en.wikipedia.org/wiki/List_of_HTTP_status_codes).

No teste seguinte, confirmo se a resposta recebida é a esperada, considerando os dados registrados no `ModelForm` do `setUp`.

```python
# testes.py
class FenomenoGeoJsonTest(TestCase):
    def setUp(self):
        self.form = FenomenoForm({
            'nome': 'Teste',
            'data': '2020-01-01',
            'hora': '09:12:12',
            'longitude': -42,
            'latitude': -22})
        self.form.save()

    def teste_geojson_status_code(self):
        self.resp = self.client.get('/geojson/')
        self.assertEqual(200, self.resp.status_code)

    def teste_geojson_FeatureCollection(self):
        self.resp = self.client.get(r('geojson'))
        self.assertEqual(self.resp.json(), {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {"popup_content": "<strong><span>Nome: </span>Teste</strong></p>", "model": "core.fenomeno"}, "id": 1, "geometry": {"type": "Point", "coordinates": [-42.0, -22.0]}}], "crs": {"type": "name", "properties": {"name": "EPSG:4326"}}})

```

Obviamente, ambos testes falharão, pois ainda não criamos a view, nem a designamos a um *path* do nosso sistema.

Para fazê-los passar, vamos primeiro criar a view. Em `views.py` uma classe nova, herdando da classe `GeoJSONLayerView`. Ela será a view responsável por nos servir os dados do projeto já em `geojson` que serão consumidos em um *webmap*.

Percebam que eu já estou considerando que o `geojson` virá com uma `properties`, ainda a ser criada no model em questão e que terá nome de `popup-content`. Poderíamos adicionar a essa `property` quantas informaçções acharmos pertinente a ser apresentada no *popup* do mapa. Por agora estou apenas informando o nome do fenômeno mapeado.

Um último detalhe é que, como estamos usando um `Class Based-View`, ao final a convertemos em view, com o método `as_view()`.

```python
# views.py
from djgeojson.views import GeoJSONLayerView

from map_proj.core.models import Fenomeno


class FenomenoGeoJson(GeoJSONLayerView):
    model = Fenomeno
    properties = ('popup_content',)

    def get_queryset(self):
        context = Fenomeno.objects.all()
        return context

fenomeno_geojson = FenomenoGeoJson.as_view()
```

### Adicionando propriedade para *popup*  

Por agora, adicionarei apenas o campo `nome` do fenômeno à propriedade do meu modelo. Mais à frente podemos incrementar, adicionando um [`get_absolute_url`](https://docs.djangoproject.com/en/3.2/ref/models/instances/#get-absolute-url) por exemplo, para poder acessar aos detalhes do fenômeno a partir do *popup* do mapa.

```python
#models.py
...
    @property
    def popup_content(self):
        popup = f'<strong><span>Nome: </span>{self.nome}</strong></p>'
        return popup
```

Para poder acessar essa view, precisamos incorporá-la na nossa `urls.py`:

```python
# urls.py
from django.contrib import admin
from django.urls import path

from map_proj.core.views import fenomeno_geojson # novo!

urlpatterns = [
    path('admin/', admin.site.urls),
    path('geojson/', fenomeno_geojson, name='geojson'), # novo!
]

```

Com isso teremos os nossos últimos testes passando. Se ainda assim você tiver curiosidade, pode acessar os dados pela *url* `http://127.0.0.1:8000/geojson/` e receberá os dados servidos em `geojson`:

```
{"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {"popup_content": "<strong><span>Nome: </span>teste</strong></p>", "model": "core.fenomeno"}, "id": 3, "geometry": {"type": "Point", "coordinates": [-42.0, -22.0]}}], "crs": {"type": "name", "properties": {"name": "EPSG:4326"}}}
```

Pronto, já temos um sistema de validação para os campo de longitude e latitude, garantindo que as coordenadas inseridas estão na região de interesse. Também já temos uma `view` nos servindo os dados em formato `geojson`. Vamos ao `leaflet`, entender como montar um *webmap*.

## Django-leaflet

Para saber mais sobre o `django-leaflet`, recomendo dar uma olhada na página [pypi](https://pypi.org/project/django-leaflet/) e na [documentação](https://django-leaflet.readthedocs.io/en/latest/installation.html). Mas, como eu estive me perguntando "por quê ter e usar um pacote `django-leaflet` se eu posso usar o [`leaflet`](https://leafletjs.com/) "puro", já que se trata de uma biblioteca JavaScript?", deixo alguns puntos que os proprios desenvolvedores apresentam na documentação:

> Main purposes of having a python package for the Leaflet Javascript library :
>  - Install and enjoy ;
>  -  Do not embed Leaflet assets in every Django project ;
>  -  Enjoy geometry edition with Leaflet form widget ;
>  -  Control apparence and settings of maps from Django settings (e.g. at deployment) ;
>  -  Reuse Leaflet map initialization code (e.g. local projections) ;

E por último, mas não menos importante, um alerta:
> note:	django-leaflet is compatible with django-geojson fields, which allow handling geographic data without spatial database.

Bem legal! ele criaram um pacote já compatível com o pacote `django-geojson`, que nos permite simular campos geográficos sem a neccessidade de toda a infraestrutura de uma base de dados de SIG (PostGIS, por exemplo).

Porém, atenção ao seguinte detalhe:
> #### Dependencies
> django-leaflet requires the GDAL library installed on the system. Installation instructions are platform-specific.

A instalação do pacote é bem simples. 

```python
pip install django-leaflet
```

E após sua instalação, é necessário inluir-lo no settings como *INSTALLED_APPS*. Não esqueça de adicioná-lo ao `requirements.txt`, também.

```python
# settings.py
INSTALLED_APPS = [
    ...
    'djgeojson',
    'leaflet', # novo
    'map_proj.core',
]
```

- add templates dir
- add map.html
- create path urls.py

```html
{% load leaflet_tags %}

<head>
    ...
    {% leaflet_js %}
    {% leaflet_css %}
</head>
```

Isso já o suficiente para ter um *webmap*, no path indicado no `urls.py`.

![](./map_proj/img/leaflet_1.png)

Adicionando um marker hardcoded:

```html
{% load leaflet_tags %}
<script>
    function map_init_basic (map, options) {

        L.marker([-22, -42]).addTo(map);

    }
</script>



<head>
    {% leaflet_js %}
    {% leaflet_css %}
</head>
<body>

<!--    {% leaflet_map "yourmap" %}-->
{% leaflet_map "yourmap" callback="window.map_init_basic" %}

</body>

```

Falta agora "linkar" a view que nos serve o geojson com o mapa em questão, bem como configurar o mapa.

Adicionando os dados a traves do geojson:

```html
{% load leaflet_tags %}

    <script>
      var dataurl = '{% url "geojson" %}';

      window.addEventListener("map:init", function (event) {
        var map = event.detail.map;
        // Download GeoJSON data with Ajax
        fetch(dataurl)
          .then(function(resp) {
            return resp.json();
          })
          .then(function(data) {
            L.geoJson(data, {
              onEachFeature: function onEachFeature(feature, layer) {
                var props = feature.properties.popup_content;
                layer.bindPopup(props);
            }}).addTo(map);
          });
      });

    </script>



<head>
    {% leaflet_js %}
    {% leaflet_css %}
</head>
<body>

{% leaflet_map "yourmap" %}

</body>

```

Mudando a tamanho do *webmap*.

```html
<style>
    #yourmap {
        width: 100%;
        height: 800px;
    }
</style>
```

### configurando leaflet

[Ver documentação](https://django-leaflet.readthedocs.io/en/latest/templates.html#configuration)

```python
# setting.py
LEAFLET_CONFIG = {
    # conf here
}
```

## Heroku
como funciona: https://dzone.com/articles/how-heroku-works


## reflexões

[The most important part of a function name is a verb. ](https://melevir.medium.com/python-functions-naming-the-algorithm-74320a18278d)