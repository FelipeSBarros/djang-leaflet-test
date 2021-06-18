# Criando um sistema para gestão de dados geográficos de forma simples e robusta II

Na [primeira publicação](https://www.linkedin.com/pulse/criando-um-sistema-para-gest%C3%A3o-de-dados-geogr%C3%A1ficos-e-felipe-/) onde exploro a possibilidade de implementar um sistema de gestão de dados geoespaciais com Django, sem a necessidade de usar um servidor com PostGIS, vimos sobre:
* o uso do [`django-geojson`](https://django-geojson.readthedocs.io/en/latest/) para simular um campo geográfico no models;
* o [`geojson`](https://geojson.readthedocs.io/en/latest/) para criar um objeto da classe *geojson* e realizar as validações necessárias para garantir robustez do sistema;  
* a criação do fomulário de registro de dados usando o [`ModelForm`](https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/#modelform);  

Agora é hora de evoluir e expandir um pouco o sistema criado. Nessa publicação vamos:  
* criar validadores de longitude e latitude para poder restringir a inserção de dados a uma determinada região;  
* adicionar uma propriedade ao model que será usada no *popup* do mapa em `leaflet`;  
* instalar e usar o [`django-leaflet`](https://django-leaflet.readthedocs.io/en/latest/) para poder usar o `widget` além de outras funcionalidades;  
* criar uma view para visualizar os dados em mapas usando `GeoJSONLayerView`, do [`django-geojson`](https://django-geojson.readthedocs.io/en/latest/);  
* Tudo isso testando se tais funcionalidades ou propriedades estão com o comportamento esperado;  
* fazer deploy no [heroku](heroku.com)(?)  
    * Um argumento para fazê-lo é levar a implementação até o final.  
    * O leaflet depende de funcionalidades do GDAL. E o heroku possui o [heroku-geo-buildpack](https://github.com/heroku/heroku-geo-buildpack) para isso :heart:  

Vamos lá!

## criando validadores de longitude e latitude  

### Sobre os validadores:  
Os validadores ([`validators`](https://docs.djangoproject.com/en/3.2/ref/forms/validation/#validators) ) fazem parte do sistema de validação de formulários e de campos do Django. Ao criarmos campos de uma determinada classe em nosso model, como por exemplo `integer`, o django cuidará automaticamente da validação do valor passado a este campo pelo formulário, retornando um erro quando o usuário ingressar um valor de texto no campo em questão. O interessante é que além dos validadores já implementados para cada classe, podemos criar outros, conforme nossa necessidade.

> Por que necesitamos um validador de `latitude` e `longitude`?

Como estou explorando o desenvolvimento de um sistema de gestão de dados goegráficos com recursos limitados, ou seja, sem uma infraestrutura de operações e consultas espaciais, não poderei consultar se o par de coordenadas inserido pelo usuário está contido nos limites de um determinado estado (uma operação clássica com dados geográficos). E não ter essa possibilidade de validação poderá colocar em risco a qualidade do dado inserido.

E como não se abre mão quando a questão é qualidade, uma saída será a criação de validadores personalizados para os campos de `latitude` e `logitude`, garantindo que esses possuem valores condizentes à nossa área de interesse.

**O que precisamos saber:**
os `validators` são funções que recebem um valor, apenas, o valor inserido pelo usuário no campo a ser validado, que passará por uma lógica de validação retornando um [`ValidationError`](https://docs.djangoproject.com/en/3.2/ref/forms/validation/#raising-validation-error) quando o valor inserido não passar nos testes. Com o `ValidationError` podemos customizar uma mensagem de erro, indicando ao usuário o motivo do valor não ter sido considerado válido.  

Então, criarei validadores dos campos de `latitude` e `longitude` para sempre que entrarem com valores que não contemplem a área do estado do Rio de Janeiro, um `ValidationError` será retornado.  

> :warning: Essa não é uma solução ótima já que, dessa forma, estaremos considerando o bounding box do estado em questão, e com isso haverão algumas áreas onde as coordenadas serão válidas, ainda que não estejam internas ao território estadual. Ainda assim, acredito que seja uma solução boa suficiente para alguns casos, principalmente por não depender de toda infraestrutura de GIS.

**O que é um `bouding box`?**  
Bounding box poderia ser traduzido por "retângulo envolvente" do estado, ou de uma feição espacial. Na imagem a baixo, vemos o território do estado do Rio de Janeiro e o retângulo envolvente que limita as suas coordenadas máximas e mínimas de longitude e latitude.  

![](./map_proj/img/RJ_bbox.png)

Percebam que, como mencionado antes, o que conseguimos garantir é que os pares de coordenadas estejam em alguma área interna ao retângulo em questão o que não garante que as mesmas estejam no território do estado do Rio de Janeiro.

## Criando os testes:

Antes de tudo, criamos os testes.
Para isso, criarei uma função chamada `update_values` que receberá um `**kwargs`, que é uma forma de passar a uma função um conjunto de valores nomeados. Nessa função, crio um dicionário tendo como chave os nomes dos campos do meu `ModelForm`, e como valores, os valores esperados a cada campo.

Logo em seguida, crio um objeto chamado `finalData` que será o dicionário `validForm` criado anteriormente, mas com os parâmetros nomeados passados como `**kwargs` da função. Esse dicionário com os valores atualizados serão usadas para instanciar o meu `ModelForm` que será retornado ao fim da execussão.

Eu fiz isso para poder ir, a cada teste, atualizando apenas os campos que quero simular valores a serem validados, sem ter que instanciar è passar sempre os valores do `ModelForm`.
```python
class FenomenoFormValidatorsTest(TestCase):
    def update_values(self, **kwargs):
        validForm = {  # valid form
            'nome': 'Teste',
            'data': '2020-01-01',
            'hora': '09:12:12',
            'longitude': -42,
            'latitude': -21}

        finalData = dict(validForm, **kwargs)
        form = FenomenoForm(finalData)
        return form
```
Assim, eu posso criar diferentes métodos de test case, usando o método criando anteriormente para alterar o valor iniciar a um que deva ser considerado inválido pelo validador.

Nos método uso o `assertEqual` para confirmar que o o texto do `AssertError` é o que esperamos. Para saber sobre outros [`assertions`](https://docs.python.org/3/library/unittest.html#unittest.TestCase.debug)

```python
    def test_max_longitude(self):
        form = self.update_values(longitude='-45')
        form.is_valid()
        self.assertEqual(form.errors["longitude"][0], 'Coordenada longitude fora do contexto do estado do Rio de Janeiro')

    def test_min_longitude(self):
        form = self.update_values(longitude='-40')
        form.is_valid()
        self.assertEqual(form.errors["longitude"][0], 'Coordenada longitude fora do contexto do estado do Rio de Janeiro')

    def test_max_latitude(self):
        form = self.update_values(latitude='-24')
        form.is_valid()
        self.assertEqual(form.errors["latitude"][0], 'Coordenada latitude fora do contexto do estado do Rio de Janeiro')

    def test_min_latitude(self):
        form = self.update_values(latitude='-19')
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

Ou seja, o `forms` após ser validado deveria conter um atributo `errors` tendo como chave o nome do campo que apresentou dados inválidos. Como não temos os validadores criados, ainda, os campos `latitude` não foi encontrado pelo teste executado.

~~Como podemos definir vários validadores para um mesmo campo, o `value` esperado é uma lista. O erro retorna exatamente a inexistencia de uma chave com o nome latitude, indicando que não houve qualquer problema de validação.~~

## Criando e usando validadores:

Para superá-los, criamos, enfim, os validadores:
```python
from django.core.exceptions import ValidationError


def validate_longitude(lon):
    if lon < -44.887212 or lon > -40.95975:
        raise ValidationError("Coordenada longitude fora do contexto do estado do Rio de Janeiro", "erro longitude")

def validate_latitude(lat):
    if lat < -23.366868 or lat > -20.764962:
        raise ValidationError("Coordenada latitude fora do contexto do estado do Rio de Janeiro", "erro latitude")
```
Com esses validadores estou garantindo que ambos latitude e longitude estajm na área de interesse e caso contrário, retorno um erro informando ao usuário.

E é preciso adicioná-los ao forms para que sejam usados:

```python
class FenomenoForm(ModelForm):
    longitude = FloatField(validators=[validate_longitude])
    latitude = FloatField(validators=[validate_latitude])
...
```
No desenvlvimento dessa solução, tive alguns incovenientes pois ao informar uma latitude ou longitude que não passase pela validação (justamente para confirmar que isso aconteceria e o usuário receberia a mensagem de erro), passei a ter um erro no método clean, já que é nele que o campo `geom` recebe os valores de `longitude` e `latitude` formando uma classe `geojson`. E ao não ter um desses valores, acabei tendo dois erros: o de validação do campo e o de validação do campo `geom`.
Para evitar isso, fiz com que o campo `geom` só seja criado e validado no método clea, quando ambos valores (longitude e latitude) existam. Ou seja, tenham passado pelos validadores.

```python
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

## View GeoJSONLayerView
[sobre serializador](https://django-portuguese.readthedocs.io/en/1.0/topics/serialization.html)

[GeoJSONLayerView](https://django-geojson.readthedocs.io/en/latest/views.html#geojson-layer-view)

```python
# urls.py
from djgeojson.views import GeoJSONLayerView
...
url(r'^data.geojson$', GeoJSONLayerView.as_view(model=MushroomSpot), name='data'),
```

```python
# Leaflet JS
var layer = L.geoJson();
map.addLayer(layer);
$.getJSON("{% url 'data' %}", function (data) {
    layer.addData(data);
});
```
```python
# views.py
from djgeojson.views import GeoJSONLayerView

class MapLayer(GeoJSONLayerView):
    # Options
    precision = 4   # float
    simplify = 0.5  # generalization


# urls.py
from .views import MapLayer, MeetingLayer
...
url(r'^mushrooms.geojson$', MapLayer.as_view(model=MushroomSpot, properties=('name',)), name='mushrooms')
```

#### Add statics urls

```python
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR
```


