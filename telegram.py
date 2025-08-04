!pip install telebot # Instalando a lib do telegram para bot
!pip install google-generativeai # Já vamos deixar a lib do generativeai já instalado para o passo final

# Importando as bibliotecas
import google.generativeai as genai
import telebot
from datetime import datetime

# Chamando o bot pela chave API dele, depois desse momento basta chamar o bot e pedir a ele os comandos
bot = telebot.TeleBot('7 pega a chave api do bot no Bot Father do Telegram s')

# Aqui definimos o nome do comando, nesse caso para chamar o comando 'tarefa' basta digitar '/tarefa' no chat do bot
@bot.message_handler(commands=['tarefa'])

# A primeira função serve para iniciar o comando, chamando a função de carregar o arquivo txt de armazenamento, ou criando ele se não o encontrar
def funcao (message):
  def carregar_tarefas():
    global tarefas
    try:
      with open('tarefas.txt', 'r') as f:
        linhas = f.readlines()
        tarefas = {}
        for linha in linhas:
          if linha.strip():
            partes = linha.strip().split(';')
            if len(partes) == 3:
              try:
                id_tarefa = int(partes[0])
                descricao = partes[1]
                prazo_str = partes[2]
                prazo = datetime.strptime(prazo_str, "%d-%m-%Y").date()
                tarefas[id_tarefa] = {'descricao': descricao, 'prazo': prazo}
              except ValueError:
                print(f"Pulando linha inválida ao carregar: {linha}")
        print("Tarefas carregadas com sucesso!")
    except FileNotFoundError:
      print("Arquivo de tarefas não encontrado. Começando com lista vazia.")
      tarefas = {}
    except Exception as e:
      print(f"Erro ao carregar tarefas: {e}")
      tarefas = {}

  bot.send_message(message.chat.id, # ao final da função é enviada a lista de funções disponíveis para o usuário selecionar
  """\n--- Organizador de Tarefas ---\n
  1. Adicionar Tarefa
  2. Visualizar Tarefas
  3. Atualizar Tarefa
  4. Apagar Tarefa
  5. Me ajude com essa tarefa
  6. Salvar e Encerrar
  \nEscolha uma opção!""")
  carregar_tarefas()
  bot.register_next_step_handler(message, selecao)

def selecao(message): # Função que direciona o usuário para a opção desejada ou encerra o app
  escolha = message.text
  if escolha == "1":
    bot.send_message(message.chat.id, "Digite a tarefa que deseja adicionar:")
    bot.register_next_step_handler(message, adicionar_tarefa)
  elif escolha == "2":
    ver_tarefas(message)
  elif escolha == "3":
    atualizar_id_tarefa_pedido(message)
  elif  escolha == "4":
    comando_apagar_tarefa(message)
  elif escolha == "5":
    me_ajude_com_tarefa_pedido(message)
  elif escolha == "6":
    bot.send_message(message.chat.id, "Obrigado por utilizar o Organizador de Tarefas!")
  else:
    bot.send_message(message.chat.id, "Opção inválida. Por favor, escolha uma das opções listadas.")
    funcao(message) # Retorna para o menu principal

def adicionar_tarefa(message): # Começa a rotina de adicionar nova tarefa
  descricao_tarefa = message.text
  bot.send_message(message.chat.id, "Digite a data de entrega (formato DD-MM-YYYY):")
  bot.register_next_step_handler(message, lambda msg: salvar_tarefa(msg, descricao_tarefa))

def salvar_tarefa(message, descricao_tarefa): # Finaliza a adição de nova tarefa  com o salvamento em arquivo txt
  prazo_string = message.text
  try:
    prazo = datetime.strptime(prazo_string, "%d-%m-%Y").date()
    id_tarefa = len(tarefas) + 1
    tarefas[id_tarefa] = {'descricao': descricao_tarefa, 'prazo': prazo}
    bot.send_message(message.chat.id, f"Tarefa '{descricao_tarefa}' adicionada com sucesso com data de entrega {prazo_string}!")
    with open('tarefas.txt', 'w') as f:
      for id_tarefa, informacao_tarefa in tarefas.items():
        f.write(f"{id_tarefa};{informacao_tarefa['descricao']};{informacao_tarefa['prazo'].strftime('%d-%m-%Y')}\n")
    bot.send_message(message.chat.id, "Tarefas salvas com sucesso!")
    funcao(message) # Faz o retorno ao menu principal após concluir o salvamento
  except ValueError:
    bot.send_message(message.chat.id, "Formato de data inválido. Use DD-MM-YYYY.")
    bot.send_message(message.chat.id, "Digite a data de entrega (formato DD-MM-YYYY):")
    bot.register_next_step_handler(message, lambda msg: salvar_tarefa(msg, descricao_tarefa))
    bot.send_message(message.chat.id, f"Erro ao salvar tarefas: {e}")

def ver_tarefas(message): #Exibe ou uma lista de tarefas adicionadas ou uma mensagem informando que a lista está vazia
  if len(tarefas) == 0:
    bot.send_message(message.chat.id, "Nenhuma tarefa adicionada ainda.")
  else:
    response = "Suas Tarefas:\n"
    for id_tarefa, informacao_tarefa in tarefas.items():
      response += f"{id_tarefa}. {informacao_tarefa['descricao']} (Entrega: {informacao_tarefa['prazo'].strftime('%d-%m-%Y')}\n"
    bot.send_message(message.chat.id, response)
  funcao(message) # Faz o retorno ao menu principal após exibir ou a lista com tarefas, ou a mensagem de nenhuma tarefa

def atualizar_id_tarefa_pedido(message): # Inicia o processo de atualizar tarefa
  if not tarefas:
    bot.send_message(message.chat.id, "Nenhuma tarefa para atualizar.")
    funcao(message)
    return
  bot.send_message(message.chat.id, "Digite o ID da tarefa que deseja atualizar:") # Primeiro pede ID...
  bot.register_next_step_handler(message, selecionar_campo_atualizar_tarefa)

def selecionar_campo_atualizar_tarefa(message): 
  try:
    id_tarefa_a_atualizar = int(message.text)
    if id_tarefa_a_atualizar in tarefas:
      bot.send_message(message.chat.id, f"Tarefa selecionada: {tarefas[id_tarefa_a_atualizar]['descricao']}")
      bot.send_message(message.chat.id, "O que deseja atualizar? (descricao/data):") #... depois o que atualizar, descrição da tarefa ou o prazo de entrega
      bot.register_next_step_handler(message, lambda msg: atualizar_tarefa(msg, id_tarefa_a_atualizar))
    else:
      bot.send_message(message.chat.id, "ID de tarefa inválido.")
      funcao(message)
  except ValueError:
      bot.send_message(message.chat.id, "Entrada inválida. Por favor, digite um número.")
      funcao(message)

def atualizar_tarefa(message, id_tarefa):
  campo_a_atualizar = message.text.lower()
  if campo_a_atualizar == 'descricao': # Se for a descrição...
    bot.send_message(message.chat.id, "Digite a nova descrição da tarefa:")
    with open('tarefas.txt', 'w') as f:
      for id_tarefa, informacao_tarefa in tarefas.items():
        f.write(f"{id_tarefa};{informacao_tarefa['descricao']};{informacao_tarefa['prazo'].strftime('%d-%m-%Y')}\n")
    bot.register_next_step_handler(message, lambda msg: salvar_tarefa_atualizada(msg, id_tarefa, 'descricao'))
  elif campo_a_atualizar == 'data':
    bot.send_message(message.chat.id, "Digite a nova data de entrega (formato DD-MM-YYYY):") # ...ou a data de entrega    
    with open('tarefas.txt', 'w') as f:
      for id_tarefa, informacao_tarefa in tarefas.items():
        f.write(f"{id_tarefa};{informacao_tarefa['descricao']};{informacao_tarefa['prazo'].strftime('%d-%m-%Y')}\n")
    bot.register_next_step_handler(message, lambda msg: salvar_tarefa_atualizada(msg, id_tarefa, 'prazo'))
  else:
    bot.send_message(message.chat.id, "Campo inválido. Por favor, digite 'descricao' ou 'data'.")
    selecionar_campo_atualizar_tarefa(message)

def salvar_tarefa_atualizada(message, id_tarefa, field): # Salva a tarefa atualizada
  novo_valor = message.text
  if field == 'prazo':
    try:
      novo_valor = datetime.strptime(novo_valor, "%d-%m-%Y").date()
      tarefas[id_tarefa][field] = novo_valor
      with open('tarefas.txt', 'w') as f:
        for id_tarefa, informacao_tarefa in tarefas.items():
          f.write(f"{id_tarefa};{informacao_tarefa['descricao']};{informacao_tarefa['prazo'].strftime('%d-%m-%Y')}\n")
      bot.send_message(message.chat.id, "Tarefa atualizada com sucesso!")
    except ValueError:
      bot.send_message(message.chat.id, "Formato de data inválido. Use DD-MM-YYYY.")
      bot.send_message(message.chat.id, "Digite a nova data de entrega (formato DD-MM-YYYY):")
      bot.register_next_step_handler(message, lambda msg: salvar_tarefa_atualizada(msg, id_tarefa, 'prazo'))
      return
  else:
    tarefas[id_tarefa][field] = novo_valor
    with open('tarefas.txt', 'w') as f:
      for id_tarefa, informacao_tarefa in tarefas.items():
        f.write(f"{id_tarefa};{informacao_tarefa['descricao']};{informacao_tarefa['prazo'].strftime('%d-%m-%Y')}\n")
    bot.send_message(message.chat.id, "Tarefa atualizada com sucesso!")
  funcao(message) # Retorna ao menu principal

def comando_apagar_tarefa(message): # Comando para apagar alguma tarefa, primeiro seleciona a ID da tarefa ...
  if not tarefas:
    bot.send_message(message.chat.id, "Nenhuma tarefa para apagar.")
    funcao(message)
    return
  bot.send_message(message.chat.id, "Digite o ID da tarefa que deseja apagar:")
  bot.register_next_step_handler(message, apagar_tarefa)

def apagar_tarefa(message): # .. e apaga a tarefa em si, ...
  try:
    id_tarefa_a_deletar = int(message.text)
    if id_tarefa_a_deletar in tarefas:
      tarefa_deletada = tarefas.pop(id_tarefa_a_deletar)
      bot.send_message(message.chat.id, f"Tarefa '{tarefa_deletada['descricao']}' apagada com sucesso!")
      # ...salva o arquivo após deletar a tarefa
      with open('tarefas.txt', 'w') as f:
        for id_tarefa, informacao_tarefa in tarefas.items():
          f.write(f"{id_tarefa};{informacao_tarefa['descricao']};{informacao_tarefa['prazo'].strftime('%d-%m-%Y')}\n")
      bot.send_message(message.chat.id, "Tarefas salvas com sucesso após a exclusão!")
    else:
      bot.send_message(message.chat.id, "ID de tarefa inválido.")
    funcao(message) # Volta para o menu principal
  except ValueError:
    bot.send_message(message.chat.id, "Entrada inválida. Por favor, digite um número.")
    funcao(message)
  except Exception as e:
    bot.send_message(message.chat.id, f"Erro ao apagar ou salvar tarefas: {e}")
    funcao(message)

# Configure a sua chave de API do Gemini (substitua 'YOUR_API_KEY' pela sua chave real)

genai.configure(api_key="A pega a chave api do gemini M")

def me_ajude_com_tarefa_pedido(message): # Pede ajuda para o GEMINI para a tarefa
  if not tarefas:
    bot.send_message(message.chat.id, "Nenhuma tarefa adicionada ainda para pedir ajuda.")
    funcao(message)
    return
  bot.send_message(message.chat.id, "Digite o ID da tarefa para a qual deseja ajuda:")
  bot.register_next_step_handler(message, obter_ajuda_ia)

def obter_ajuda_ia(message):
  try:
    id_tarefa_ajuda = int(message.text)
    if id_tarefa_ajuda in tarefas:
      descricao_tarefa = tarefas[id_tarefa_ajuda]['descricao']
      prompt = f"Me ajude com a seguinte tarefa: {descricao_tarefa}" # Constroi o prompt usando a frase "Me ajude com a seguinte tarefa: + a descrição da tarefa"
      try:
        model = genai.GenerativeModel('gemini-1.5-flash') # Seleciona o modelo da IA
        response = model.generate_content(prompt)
        if response and response.text:
          bot.send_message(message.chat.id, f"Resposta da IA para a tarefa {id_tarefa_ajuda}:\n{response.text}")
        else:
          bot.send_message(message.chat.id, "Não foi possível obter uma resposta da IA para esta tarefa.")
      except Exception as e:
        bot.send_message(message.chat.id, f"Erro ao interagir com a API de IA: {e}")
    else:
      bot.send_message(message.chat.id, "ID de tarefa inválido.")
    funcao(message) # Retorna ao menu principal
  except ValueError:
    bot.send_message(message.chat.id, "Entrada inválida. Por favor, digite um número.")
    funcao(message)

bot.infinity_polling() # Comando que mantém o aplicativo ativo
