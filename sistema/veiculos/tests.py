from django.test import TestCase, Client
from django.urls import reverse
from veiculos.models import *
from veiculos.forms import *
from datetime import datetime
from django.contrib.auth.models import User

class TestesModelVeiculo(TestCase):
    def setUp(self):
        self.veiculo = Veiculo.objects.create(
            marca=1,
            modelo='Fusca',
            ano=datetime.now().year,
            cor=2,
            combustivel=3
        )

    def test_is_new(self):
        self.assertTrue(self.veiculo.veiculo_novo)
        self.veiculo.ano = datetime.now().year - 5
        self.assertFalse(self.veiculo.veiculo_novo)

    def test_anos_de_uso(self):
        # 1. Garante que o carro novo (criado no setUp com o ano atual) tem 0 anos de uso
        self.assertEqual(self.veiculo.anos_de_uso(), 0)
        
        # 2. Envelhece o carro em 10 anos
        self.veiculo.ano = datetime.now().year - 10
        self.veiculo.save() # Salva no banco de dados temporário
        
        # 3. Agora testa se o método calcula corretamente os 10 anos
        self.assertEqual(self.veiculo.anos_de_uso(), 10)

class TestesViewListarVeiculo(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.force_login(self.user)
        self.url = reverse('listar-veiculos')
        self.veiculo = Veiculo.objects.create(
            marca=1,
            modelo='Fusca',
            ano=datetime.now().year,
            cor=2,
            combustivel=3
        )

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context.get('veiculos')), 1) # Corrigido .get[] para .get()

class TestesViewCriarVeiculos(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.force_login(self.user)
        self.url = reverse('criar-veiculos')
        self.form_data = {
            'marca': 1,
            'modelo': 'Fusca',
            'ano': datetime.now().year,
            'cor': 2,
            'combustivel': 3
        }

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        # O Django CreateView espera um POST. Aqui estamos simulando o envio do formulário
        response = self.client.post(self.url, data=self.form_data)
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('listar-veiculos'))

        # Como criamos 1 veículo com o form_data, verificamos se ele está no banco
        self.assertEqual(Veiculo.objects.count(), 1)
        self.assertEqual(Veiculo.objects.first().modelo, 'Fusca')

class TestesViewEditarVeiculos(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.force_login(self.user)
        self.veiculo = Veiculo.objects.create(
            marca=1,
            modelo='Kombi', # Nome original do carro
            ano=datetime.now().year,
            cor=2,
            combustivel=3
        )
        self.url = reverse('editar-veiculos', kwargs={'pk': self.veiculo.pk})
        self.form_data = {
            'marca': 1,
            'modelo': 'Fusca', # Novo nome que queremos alterar
            'ano': datetime.now().year,
            'cor': 2,
            'combustivel': 3
        }

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        response = self.client.post(self.url, data=self.form_data)
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('listar-veiculos'))

        veiculo_atualizado = Veiculo.objects.get(id=self.veiculo.id)
        self.assertEqual(veiculo_atualizado.modelo, 'Fusca')

class TestesViewExcluirVeiculos(TestCase):
    def setUp(self):
        self.client = Client()
        # Cria um usuário e faz login (necessário se a view usar LoginRequiredMixin)
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.force_login(self.user)
        
        # Cria um veículo no banco de dados de teste
        self.veiculo = Veiculo.objects.create(
            marca=1,
            modelo='Opala',
            ano=1978,
            cor=2,
            combustivel=3
        )
        # Monta a URL passando a chave primária (pk) do veículo recém-criado
        self.url = reverse('excluir-veiculos', kwargs={'pk': self.veiculo.pk})

    def test_get(self):
        # Testa se a página de confirmação de exclusão abre corretamente
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        # Dispara um POST para confirmar a exclusão
        response = self.client.post(self.url)
        
        # O DeleteView padrão redireciona após o sucesso (status 302)
        self.assertEqual(response.status_code, 302)
        
        # Verifica se redirecionou para a página correta 
        self.assertRedirects(response, reverse('listar-veiculos'))
        
        # Verifica no banco de dados se a contagem de veículos agora é zero
        self.assertEqual(Veiculo.objects.count(), 0)