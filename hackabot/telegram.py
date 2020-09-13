import collections
import logging
import threading
import subprocess
from pathlib import Path
from threading import Lock
from typing import Any, DefaultDict

import requests
import telebot
import granula
import soundfile

logger = logging.getLogger('telegram')
import sys
sys.path.append("voicekit-examples/python")

from tinkoff.cloud.stt.v1 import stt_pb2_grpc, stt_pb2
from tinkoff.cloud.tts.v1 import tts_pb2_grpc, tts_pb2
from auth import authorization_metadata
import grpc
import os
import wave
import json
from Tinkoff import all_information
import plotly.graph_objects as go
from PIL import Image, ImageDraw

def printbar(salary, upperbound):
    im = Image.open('progress.png').convert('RGB')
    draw = ImageDraw.Draw(im)

    # Cyan-ish fill colour
    color=(98,211,245)

    n = upperbound
    ca = salary
    x_n = 600
    # Draw circle at right end of progress bar
    x, y, diam = ca*x_n/n, 8, 34
    draw.ellipse([x,y,x+diam,y+diam], fill=color)

    # Flood-fill from extreme left of progress bar area to behind circle
    ImageDraw.floodfill(im, xy=(14,24), value=color, thresh=40)
    draw.text((5,20), "0", fill=(255,255,0))
    draw.text((x+20,20), str(ca), fill=(255,255,0))
    draw.text((600,20), str(n), fill=(255,255,0))

    # Save result
    im.save('fig1.png')

def func_fig(max_amount_of_momey, amount_of_money):
    fig = go.Figure(
        data=[go.Bar(x=['Amount of money'], y=[max_amount_of_momey], showlegend=False, marker_color='grey')])
    fig.add_trace(go.Bar(x=['Amount of money'], y=[amount_of_money], text = amount_of_money, textposition='auto', showlegend=False, marker_color='gold'))
    fig.update_layout(barmode='overlay')
    fig.write_image("fig1.png")
import soundfile as sf   #   pip install pysoundfile

endpoint = os.environ.get("VOICEKIT_ENDPOINT") or "stt.tinkoff.ru:443"
api_key = os.environ["VOICEKIT_API_KEY"]
secret_key = os.environ["VOICEKIT_SECRET_KEY"]

listo = ''
for i,x in enumerate(all_information(66535)[2]):
    listo += str(i+1)+') ' + x + '\n'

stage_dict = {1:'Привет! Я Олег, ваш голосовой помощник в увлекательной финансовой игре, цель которой научить вас управлять своими деньгами. Постой, не стоит так сразу открывать мобильный банк чтобы купить непонятную акцию. Давай начнем с простого, попробуй управлять финансами моего друга - Ивана. Иван ничего не знает о контроле расходов и инвестициях, вместе с ним в ходе обучающих игр ты приобретешь необходимые навыки. Скучно не будет! За успешное прохождение заданий ты будешь получать бонусы и кэшбэк. Ну что, начнем?\n\
Варианты ответа: Да/Нет',
2:'Финансы неотъемлемая часть жизни человека. С самого рождения и до глубокой старости нас сопровождают доходы и расходы. Грамотное распределение денежных потоков позволяет экономить денежные средства и вкладывать их ценные бумаги. В ходе игры я научу тебя это делать. Перейдем к практике?\n\
Варианты ответа: Да/Нет',
3:'Планировать свой бюджет довольно просто, для этого необходимо оценить потоки расходов и доходов.\n\
Как вы думаете, при каком уровне дохода на одного человека в месяц нужно начинать планирование семейного бюджета?\n\
Варианты ответа:\n\
1)от 7 до 15 тыс. рублей\n\
2)т 15 до 30 тыс. рублей\n\
3)от 30 до 100 тыс. рублей\n\
4)более 100 тыс. рублей\n\
5)планирование не нужно\n\
6)независимо от уровня дохода',
4:'Совершенно верно,планирование бюджета - обязательный инструмент при любом уровне дохода. Готов двигаться дальше?\n\
Варианты ответа: Да/Нет',
5:'Неверно, правильный ответ 6, планирование бюджета - обязательный инструмент при любом уровне дохода. Запомни это обязательно! Готов двигаться дальше?\n\
Варианты ответа: Да/Нет',
6:'Теперь расскажу немного об инвестициях. Финансовые инвестиции - это вложение средств с целью получения дохода. Другими словами, инвестирование - это процесс, когда деньги работают и приносят еще больше денег.\n\
Если ваши сбережения лежат под подушкой, что станет с ними через 5 лет?\n\
Варианты ответа:\n\
1)Будут стоить столько же\n\
2)Будут стоить больше\n\
3)Будут стоить меньше\n',
7:'Совершенно верно,если деньги просто будут лежать под подушкой их стоимость уменьшается из-за инфляции. Готов двигаться дальше?\n\
Варианты ответа: Да/Нет',
8:'Неверно, правильный ответ 3, если деньги просто будут лежать под подушкой их стоимость уменьшается из-за инфляции. Запомни это обязательно! Готов двигаться дальше?\n\
Варианты ответа: Да/Нет',
9:'Вижу ты уже немного устал,но твой труд будет вознагражден. Держи первый бонус!\n\
Добро пожаловать на 1 уровень! Сейчас мы проверим, знаешь ли ты на сколько реально снижается стоимость денег из-за инфляции. \n\
Представьте, что у вас под матрасом с 2014 года лежит миллион рублей. Представили? Деньги все это время подъедала инфляция — прошло пять лет, под матрасом тот же миллион рублей, но купить на него сейчас можно меньше, чем в 2014 году. Угадайте, сколько нужно денег в этом году, чтобы купить столько же, сколько на миллион пять лет назад?\n\
Варианты ответа:\n\
1)1,5 миллиона\n\
2)1,4 миллиона\n\
3)1,1 миллиона\n\
4)1,2 миллиона\n\
5)1,3 миллиона\n',
10:'Неверно, правильный ответ 2, ты не поверишь, но инфляция за это время действительно составила 40 %. Представь, сколько денег съел твой матрас Запомни это обязательно! Готов двигаться дальше?\n\
Варианты ответа: Да/Нет',
11:'Совершенно верно, инфляция за это время действительно составила 40 %. Представь, сколько денег съел твой матрас. Готов двигаться дальше?\n\
Варианты ответа: Да/Нет',
12:'Кажется мы немного забыли про нашего друга Ивана. Знакомься, это Иван. Иван не совсем обычный житель нашей страны, потому что он получает зарплату в специальной валюте “тиник”. Чтобы тебе было проще, предположим, что 1 тиник =1 рублю. С последней зарплаты у него осталось 7000 тиников. Сегодня он встречается с девушкой. Как это событие может повлиять не его расходы? Интересно?\n\
Варианты ответа: Да/Нет',
13:'Сам Иван простой парень и не прочь просто прогуляться и поесть мороженного. Но какое первое впечатление он произведет на девушку? Что же выбрать?\n\
1)Прогулка в парке и мороженное\n\
2)Хороший ресторан',
14:'вы неплохо провели вечер и потратили всего 300 тиников. Девушка довольна, значит адекватная',
15:'в ресторане девушка совсем потеряла голову и заказала на 2000 тиников. Теперь до следующей зарплаты ты будешь есть только дошик, увы. Но зато выпендрился.',
16:'Оказалось,что девушка использовала вас. Вы рассторены и подавлены. Что вероятнее всего произойдет? \n\
Выберете вариант: \n\
1) Напьетесь в баре и просадите оставшиеся деньги\n\
2)Спокойно переживете это и задумаетесь о своих расходах',
17:'Ну все, теперь придется занимать денег у друзей и родственников чтобы дотянуть до зарплаты. Кто это сделал?',
18:'Начнете изучать инструменты планирования бюджета. Да?',
19: 'Ты молодец!  Вижу ты умеешь смотреть вперед, избегая неразумных расходов. Получай бонусные тиники для следующего уровня. Назначаем тебе уровень 2!',
20: 'Я бы не сказал,что ты умеешь грамотно распоряжаться своими деньгами. Тебе есть чему научиться, чем мы и займемся дальше. Я компенсирую твои траты. Но в первый и последний раз. Помни,в жизни такого не бывает. Получай повышение!',
21: 'Девушка вроде не привередливая, может потратить деньги на себя? Купить  the last of us 2?\n\
1)Да\n\
2)Нет',
22: 'Ты купил игру за 3000 тиников. Теперь у тебя совсем не осталось денег чтобы куда-то ходить. Ты отключил уведомления, круглые сутки играешь в игру. Девушка перестала предпринимать попытки связаться с тобой и ты остался один ',
23: 'Ты не купил игру, но организовал свой досуг иначе. Сходил с друзьями на футбол. Билет  стоил всего 500 тиников ',
24: 'Итак, денег оказывается достаточно, чтобы комфортно прожить месяц и начать откладывать. Но как это сделать?\
Положить под подушку на черный день? Может сделать вклад? Надо посчитать!\
Хорошо хранить деньги в укромном месте и осознавать, что всегда есть выход на черный день.\
Правда непонятно когда он будет, если вообще будет. Это значит, что деньги могут просто лежать годами и терять свою силу.\
    Лет 5 назад 25 рублей за бутылку колы было дорого, а теперь даже акционная цена не опускается ниже 35 рублей.\
    Дело в инфляции, которая в России за этот промежуток времени реально составила примерно 40%.\
Тренда на снижение не намечается, а потерять 40% от накопленных средств как-то не хочется.\
Так, есть вклады и это уже лучше, чем просто потеря от инфляции. К сожалению, реальная и\
официальная инфляция расходятся, поэтому полностью потерь не избежать.\
Что же делать? Инвестировать!\n\
1) Продолжить',
25: 'На бирже есть несколько вариантов для вклада денег. Есть акции, есть фонды, есть ETF.\
Акции - это самый непредсказуемый тип инвестирования, но он может принести высокую доходность, '
    'даже удвоить или утроить вложения за месяц. Однако, тоже самое может произойти и в другую сторону, можно почти все сразу потерять.\
Фонды - это консервативный метод инвестирования с малыми рисками и простым погружением. Таким образом можно получать чуть больше,'
    ' чем банки предлагают по вкладам.\
ETF - большой набор различных акций. За счет того, что их много, если какая-то акция упадет - другая вырастет и суммарно в \
год происходит умеренный рост. Чуть более рисковый тип вложения, чем фонды, однако, радуют годовые проценты.\
Куда будем вкладывать:\n\
1) Акции\n\
2) Фонды',
26: 'Существует просто море акций из самых различных отраслей, какие выбрать абсолютно непонятно. Могу предложить три варианта:\n\
1) Крупная стабильная компания\n\
2) Новая перспективная компания\n\
3) Средняя по размеру неприметная компания',
27: 'Cколько вкладываем?\n\
1) 100%\n\
2) 10%',
28: 'Не самый лучший выбор, надо всегда готовиться к худшему варианту. Кстати о худшем варианте, компания уже несколько недель теряет в стоимости от из-за того, что в качестве директора назначили пятилетнего ребенка. Ему надоело играть в бизнес и он уволил всех сотрудников. Акции упали на 95%. Вы потеряли почти все.\
Надо было не вестись на поводу, а изучить тему поглубже, понять как стоит инвестировать. Одно из главных правил заключается в том, что на биржу стоит выставлять не более 20% от имеющихся средств, а в определенную компанию не стоит вкладывать более 5-10% от средств на бирже. Отмотаем время назад.',
29: 'Хороший выбор, правда все равно чуточку рисковый. Одно из главных правил заключается в том, что на биржу стоит выставлять не более 20% от имеющихся средств, а в определенную компанию не стоит вкладывать более 5-10% от средств на бирже. Акции упали на 70% из-за того, что в бухгалтерии случайно перевели охраннику зарплату с семью лишними нулями на конце. Где он неизвестно, наверное охраняет лежак на мальдивах.\
Вот непорядочный охранник конечно. Хорошо, что ты вложил только 10%, а не все деньги. Наверное мне нужно узнать еще о фондах',
30: 'Сколько вкладываем?\n\
1) 100% \n\
2) 10%',
32: 'Не самый лучший выбор, надо всегда готовиться к худшему варианту. Кстати о худшем варианте, компания уже несколько недель теряет в стоимости от из-за того, что в качестве директора назначили пятилетнего ребенка. Ему надоело играть в бизнес и он уволил всех сотрудников. Акции упали на 95%. Вы потеряли почти все.\
Надо было не вестись на поводу, а изучить тему поглубже, понять как стоит инвестировать. Одно из главных правил заключается в том, что на биржу стоит выставлять не более 20% от имеющихся средств, а в определенную компанию не стоит вкладывать более 5-10% от средств на бирже.\
Отмотаем время назад',
33: 'Хороший выбор, правда все равно чуточку рисковый. Одно из главных правил заключается в том, что на биржу стоит выставлять не более 20% от имеющихся средств, а в определенную компанию не стоит вкладывать более 5-10% от средств на бирже. В этот раз повезло и акции поднялись на 5% за неделю и на 20% за месяц. Правда же классно?:)\n\
1) Наверное мне надо узнать еще о фондах\n\
2) Да, немного жалко, что не все деньги вложил, хотя с другой стороны все могло пойти ровно в другую сторону. (переход на 3 уровень)',
31: 'Инвестирование в фонды несложная задача, так как существует большое количество подборок компаний, зарекомендовавших себя как минимально рисковые. Стоит немного почитать про понравившуюся компанию и можно смело инвестировать! Однако и тут можно рискнуть. А где риск, там и прибыль. Куда положим деньги:\n\
1) Стабильная компания\n\
2) Рискованная компания',
35: 'Сколько вкладываем?\
1) 100%\n\
2) 50%',
36: 'Не самый лучший выбор, надо всегда готовиться к худшему варианту. Кстати о худшем варианте - компания случайно попала в список стабильных, если немного про нее почитать, то можно догадаться, что продавать продуктовые пакеты из чистого золота по цене пластиковых не очень выгодно. Компания обанкротилась и теперь уже деньги врядли можно вернуть. Вы потеряли все.\
Надо было не вестись на поводу, а изучить тему поглубже, понять как стоит инвестировать. Одно из главных правил заключается в том, что на биржу стоит выставлять не более 20% от имеющихся средств, а в определенную компанию не стоит вкладывать более 5-10% от средств на бирже.\
Я отмотаю время назад, а ты попробуй инвестировать иначе.',
37: 'Хороший выбор, правда все равно чуточку рисковый. Ну и хорошо, кот не рискует, тот не пьет. Компания уверенно выплатит все деньги в течении нескольких лет.\n\
1) Все как и должно быть, просто и понятно. Плохо только то, что проценты маленькие. Попробую-ка я акции.\n\
2) Это хорошее начало моей карьеры инвестора, пожалуй я погружусь в эту тему дальше',
38: 'Сколько вкладываем?\n\
1) 100%\n\
2) 50%',
39: 'Ну кто так делает? Все деньги, в непонятную компанию, ну как так? Вы потеряли почти все. Надо было не вестись на поводу, а изучить тему поглубже, понять как стоит инвестировать.\
Всегда надо изучать компанию перед тем как вложить капитал: почитать их новость, посмотреть финансовые отчеты, поискать мнения экспертов. Отмотаем время. Не повторяй ошибок.',
40: 'Хороший выбор, правда все равно чуточку рисковый. Вложение в фонд всегда долгосрочное и надо быть уверенным, что в ближайшие несколько лет компания не обанкротится. В этот раз повезло, но впредь будь внимательнее.\
1) Ну да, рисковано, но зато процентики побольше! Надо будет изучить и другие варианты инвестирования\n\
2) Так, ну вроде все попробовал, пора уже дальше двигаться',
34:'Олег: Ура! Поздравляю, Иван, ты повышен до 3 уровня. Я смотрю, тебя не остановить :)\
Давай сделаем игру реальнее. Ты получил зарплату!\
Отметишь с друзьями в баре?\
Получение зарплаты - это всегда праздник. На что потратишь свои первые деньги?\n'+ listo+'(ответь список цифр)',
41: 'Гулял, ходил в кино и ел, и весь доход твой улетел. Вот то, что у тебя осталось: '+str(round(30000 - all_information(66535)[1]))+'. Не так много, я хочу сказать. Чтобы попасть на следующий уровень, тебе нужно научиться тратить правильно и заработать m тиников. Кажется кому-то не повредит парочка советов по контролю расходов, не так ли, Иван? Давай, я тебе расскажу.\
Чтобы защитить себя от необдуманных трат, тебе нужно начать отслеживать свои покупательские привычки. Просто мониторь свои траты в течении всего месяца. Тебе нужно всего лишь записывать все, что ты тратишь. Вне зависимости от того используешь ли ты дебетовую карту, кредитную или наличные, фиксируй все свои затраты.\
Когда записываешь все свои траты, то можно наглядно увидеть, каких из них можно избежать. Давай потренируемся записывать свои затраты и впредь не тратить лишнее. Попробуй сберечь свои средства.'
}
stage_shifts = {1:{'Да':2,'Нет':1},2:{'Да':3,'Нет':2},3:{'6':4,'5':5,'4':5,'3':5,'2':5,'1':5},4:{'Да':6,'Нет':4},5:{'Да':6,'Нет':5},6:{'3':7,'2':8,'1':8},7:{'Да':9,'Нет':7},8:{'Да':9,'Нет':8},
9:{'1':10,'2':11,'3':10,'4':10,'5':10},10:{'Да':12,'Нет':10},11:{'Да':12,'Нет':11},12:{'Да':13,'Нет':12},13:{'1':14,'2':15},14:{'anything':21},
15:{'anything':16},16:{'1':17,'2':18},18:{'anything':19},17:{'anything':20},19:{'anything':24}, 20:{'anything':24}, 21:{'1': 22,'2': 23},
22:{'anything': 20},23:{'anything':19},24:{"anything":25},25:{"1":26,"2":31},26:{"1":27,"2":30,"3":27},27:{"1":28},27:{"2":29},28:{"anything":27},29:{"anything":31}, 30:{"1":32,"2":33},31:{'1':35,"2":38},
32:{"anything":30},33:{"1":31,"2":34},35:{"1":36,"2":37},36:{"anything":35},37:{"1":26,"2":34},38:{"1":39,"2":40},39:{"anything":38},40:{"1":25,"2":34}, 34:{'anything':41}}
level_money_gain = {14:[0,-300],15:[0,-2000],11:[0,1000],7:[0,1000],4:[0,1000],9:[1,3000],24:[1,0],17:[0,-2000],18:[0,2000],19:[0,6000],
22:[0,-3000],23:[0,-500],20:[0,6000],34:[1,30000],40:[0,10000], 33:[0,7000],29:[0,6000],32:[0,-3000],36:[0,-4000],39:[0,-10000], 32:[0,-5000], 35:[0,-round(all_information(66535)[1])]}
sample_rate = 48000
is_next_level = [9,24,34]

def build_request(text):
    return tts_pb2.SynthesizeSpeechRequest(
        input=tts_pb2.SynthesisInput(text=text),
        audio_config=tts_pb2.AudioConfig(
            audio_encoding=tts_pb2.LINEAR16,
            sample_rate_hertz=sample_rate,
        ),
    )


def build_first_request(sample_rate_hertz, num_channels):
    request = stt_pb2.StreamingRecognizeRequest()
    request.streaming_config.config.encoding = stt_pb2.AudioEncoding.LINEAR16
    request.streaming_config.config.sample_rate_hertz = sample_rate_hertz
    request.streaming_config.config.num_channels = num_channels
    return request

def generate_requests():
    try:
        with wave.open("voice.wav") as f:
            yield build_first_request(f.getframerate(), f.getnchannels())
            frame_samples = f.getframerate()//10 # Send 100ms at a time
            for data in iter(lambda:f.readframes(frame_samples), b''):
                request = stt_pb2.StreamingRecognizeRequest()
                request.audio_content = data
                yield request
    except Exception as e:
        print("Got exception in generate_requests", e)
        raise

def print_streaming_recognition_responses(responses):
    for response in responses:
        for result in response.results:
            print("Channel", result.recognition_result.channel)
            print("Phrase start:", result.recognition_result.start_time.ToTimedelta())
            print("Phrase end:  ", result.recognition_result.end_time.ToTimedelta())
            for alternative in result.recognition_result.alternatives:
                print('"' + alternative.transcript + '"')
            print("------------------")
            
            
            
            

def get_full_name(user: telebot.types.User) -> str:
    name = user.first_name or ''
    if user.last_name:
        name += f' {user.last_name}'
    if user.username:
        name += f' @{user.username}'
    return name


def run_bot(token: str):
    locks: DefaultDict[Any, Lock] = collections.defaultdict(threading.Lock)
    bot = telebot.TeleBot(token)
    user_stages = {}
    user_data = {}

    def _send(message: telebot.types.Message, response: str):
        bot.send_message(chat_id=message.chat.id, text=response, parse_mode='html')

    @bot.message_handler(content_types=['voice'])
    def repeat_all_message(message):
        file_info = bot.get_file(message.voice.file_id)
        file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info.file_path))
          

        
        with open('voice.ogg','wb') as f:
            f.write(file.content)
        command = ['bash','a.sh']
        res = ((subprocess.run(command,shell=False)))
        with open('tmp.txt','r') as f:
            res = json.loads(f.read())['result']
        print(res)  

        user_id = str(message.from_user.id) if message.from_user else '<unknown>'
        text = res
        
        with wave.open("synthesised123.wav", "wb") as f:
            f.setframerate(sample_rate)
            f.setnchannels(1)
            f.setsampwidth(2)

            stub = tts_pb2_grpc.TextToSpeechStub(grpc.secure_channel(endpoint, grpc.ssl_channel_credentials()))
            
            
            if user_id not in user_stages:
                user_stages[user_id]=1
                
                user_data[user_id] = [0,0]
                
                answer = stage_dict[user_stages[user_id]]
                _send(message, response=stage_dict[user_stages[user_id]])
            else:  
                printbar(user_data[user_id][1], 60000)
                photo = open('fig1.png', 'rb')
                bot.send_photo(message.chat.id, photo)             	
                _send(message, response='Ваш уровень: '+str(user_data[user_id][0])+'\nВаше количество денег:'+str(user_data[user_id][1])+"\n")             	                                    
                if 'anything' in stage_shifts[user_stages[user_id]]:
                    user_stages[user_id]= stage_shifts[user_stages[user_id]]['anything']
                    _send(message, response=stage_dict[user_stages[user_id]])
                    answer = stage_dict[user_stages[user_id]]
                else:
                    if text in stage_shifts[user_stages[user_id]]:                
                        user_stages[user_id]= stage_shifts[user_stages[user_id]][text]    
                        _send(message, response=stage_dict[user_stages[user_id]])
                        answer = stage_dict[user_stages[user_id]]
                    else:         
                        _send(message, response='Не понял тебя')
                        answer = 'Не понял тебя'
                if user_stages[user_id] in level_money_gain:
                    user_data[user_id][0]+=level_money_gain[user_stages[user_id]][0]  
                    user_data[user_id][1]+=level_money_gain[user_stages[user_id]][1]
                    #func_fig(8000, user_data[user_id][1])
                    printbar(user_data[user_id][1], 60000)
                    photo = open('fig1.png', 'rb')
                    _send(message, response='Ваш уровень:'
                                            ' '+str(user_data[user_id][0])+'\nВаше количество денег:'+str(user_data[user_id][1])+"\n")
                    bot.send_photo(message.chat.id, photo)
                if user_stages[user_id] in is_next_level:
                    photo = open('pics/'+ str(user_stages[user_id])+'.jpg', 'rb')
                    bot.send_photo(message.chat.id, photo)
                    _send(message,
                          response='А вот твой классный ПРИЗ!')
                    photo = open('pics/' + str(user_stages[user_id]) + 'r.jpg', 'rb')
                    bot.send_photo(message.chat.id, photo)
            with open('b.sh', 'w') as f:
                f.write('curl -X POST -H "Authorization: Bearer ${IAM_TOKEN}" --data-urlencode "text='+answer+'" -d "lang=ru-RU&folderId=${FOLDER_ID}" "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize" > speech.ogg')
            command = ['bash','b.sh']
            res = (subprocess.run(command, shell=False))
        voice = open('speech.ogg', 'rb')
        bot.send_voice(message.chat.id, voice)
                
        
                               
        
        #_send(message, response=res)                  

    @bot.message_handler(commands=['start'])
    def _start(message: telebot.types.Message):
        with locks[message.chat.id]:
            _send(message, response='Добро пожаловать в игру! Напишите что угодно для начала')

    def _get_echo_response(text: str, user_id: str, message) -> str:
        if user_id not in user_stages:
            user_stages[user_id] = 1

            user_data[user_id] = [0, 0]

            answer = stage_dict[user_stages[user_id]]
            return stage_dict[user_stages[user_id]]
        else:
            printbar(user_data[user_id][1], 60000)
            photo = open('fig1.png', 'rb')
            bot.send_photo(message.chat.id, photo)
            _send(message, response='Ваш уровень: ' + str(user_data[user_id][0]) + '\nВаше количество денег:' + str(
                user_data[user_id][1]) + "\n")
            if 'anything' in stage_shifts[user_stages[user_id]]:
                user_stages[user_id] = stage_shifts[user_stages[user_id]]['anything']
                if user_stages[user_id] in is_next_level:
                    photo = open('pics/'+str(user_stages[user_id])+'.jpg', 'rb')
                    bot.send_photo(message.chat.id, photo)
                    _send(message,
                          response='А вот твой классный ПРИЗ!')
                    photo = open('pics/' + str(user_stages[user_id]) + 'r.jpg', 'rb')
                    bot.send_photo(message.chat.id, photo)
                if user_stages[user_id] in level_money_gain:
                    user_data[user_id][0]+=level_money_gain[user_stages[user_id]][0]
                    user_data[user_id][1]+=level_money_gain[user_stages[user_id]][1]
                    #func_fig(8000, user_data[user_id][1])
                    printbar(user_data[user_id][1], 60000)
                    photo = open('fig1.png', 'rb')
                    _send(message, response='Ваш уровень:'
                                            ' '+str(user_data[user_id][0])+'\nВаше количество денег:'+str(user_data[user_id][1])+"\n")
                    bot.send_photo(message.chat.id, photo)
                return stage_dict[user_stages[user_id]]
            else:
                if text in stage_shifts[user_stages[user_id]]:
                    user_stages[user_id] = stage_shifts[user_stages[user_id]][text]
                    if user_stages[user_id] in is_next_level:
                        _send(message,
                              response='А вот твой классный ПРИЗ!')
                        photo = open('pics/'+ str(user_stages[user_id]) + 'r.jpg', 'rb')
                        bot.send_photo(message.chat.id, photo)
                    if user_stages[user_id] in level_money_gain:
                        user_data[user_id][0] += level_money_gain[user_stages[user_id]][0]
                        user_data[user_id][1] += level_money_gain[user_stages[user_id]][1]
                        # func_fig(8000, user_data[user_id][1])
                        printbar(user_data[user_id][1], 60000)
                        photo = open('fig1.png', 'rb')
                        _send(message, response='Ваш уровень:'
                                                ' ' + str(user_data[user_id][0]) + '\nВаше количество денег:' + str(
                            user_data[user_id][1]) + "\n")
                        bot.send_photo(message.chat.id, photo)
                    return stage_dict[user_stages[user_id]]
                else:
                    return 'Не понял тебя'
           
        #resp = requests.post('https://chitchat-vc.tinkoff.ru/?key=d812744d7bb10f374df9faa10a146ebf',json={'text': text, 'user_id': user_id})
        #return resp.text[10:-2]

    def _send_response(message: telebot.types.Message):
        chat_id = message.chat.id
        user_id = str(message.from_user.id) if message.from_user else '<unknown>'

        with locks[chat_id]:
            try:
                response = _get_echo_response(message.text, user_id, message)
            except Exception as e:
                logger.exception(e)
                response = 'Произошла ошибка'

            if response is None:
                response = 'Ответа нет'

            _send(message, response=response)

    @bot.message_handler()
    def send_response(message: telebot.types.Message):  # pylint:disable=unused-variable
        try:
            _send_response(message)
        except Exception as e:
            logger.exception(e)

    logger.info('Telegram bot started')
    bot.polling(none_stop=True)


def main():
    config_path = Path(__file__).parent / 'config.yaml'
    config = granula.Config.from_path(config_path)
    run_bot(config.telegram.key)


if __name__ == '__main__':
    while True:
        try:
            main()
        except requests.RequestException as e:
            logger.exception(e)


