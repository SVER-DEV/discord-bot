import discord
import asyncio
import os
from discord.ext import commands, tasks
import urllib
import datetime
from urllib.request import URLError
from urllib.request import HTTPError
from urllib.request import urlopen
from urllib.request import  Request, urlopen
from bs4 import BeautifulSoup
from urllib.parse import quote
import re  # Regex for youtube link
import warnings
import requests
import unicodedata
from tqdm import tqdm
import json
import time
import random
from datetime import datetime as dt
from itertools import cycle

operatoriconURLDict = dict()
client = discord.Client()

red = discord.Color.red()
green = discord.Color.green()
yellow = discord.Color.gold()
blue = discord.Color.blue()

token = 'NzIxOTg5MjM0NDk1MzI0MjUw.Xuci3w.4A_mB9rlH_67wdRlOKKtMJtqp0Y'

# for lolplayersearch
tierScore = {
    'default' : 0,
    'iron' : 1,
    'bronze' : 2,
    'silver' : 3,
    'gold' : 4,
    'platinum' : 5,
    'diamond' : 6,
    'master' : 7,
    'grandmaster' : 8,
    'challenger' : 9
}

warnings.filterwarnings(action='ignore')

opggsummonersearch = 'https://www.op.gg/summoner/userName='

#r6stats 서버에서 크롤링을 막은듯하다
r6URL = "https://r6stats.com"
playerSite = 'https://www.r6stats.com/search/'

'''
Simple Introduction about asyncio
asyncio : Asynchronous I/O. It is a module for asynchronous programming and allows CPU operations to be handled in parallel with I/O.
async def (func name)(parameters): -> This type of asynchronous function or method is called Native Co-Rutine.
- await : you can use await keyword only in Native Co-Rutine
async def add(a,b):
    print("add {0} + {1}".format(a,b))
    await asyncio.sleep(1.0)
    return a + b
async def print_add(a,b):
    result = await add(a,b)
    print("print_add : {0} + {1} = {2}".format(a,b,result))
loop = asyncio.get_event_loop()
loop.run_until_complete(print_add(1,2))
loop.close()
'''

async def catchError(message, error):
    errorCh = client.get_user(278441794633465876)

    embed = discord.Embed(title="오류 발생!", description="기능을 실행하는 동안 오류가 발생하였습니다.", color=red, timestamp=dt.utcnow())
    if message != None: embed.add_field(name="실행 중이던 명령어:", value=message.content)
    if error != None:
        error = str(error).replace("`", "")
        embed.add_field(name="오류 내용:", value=f"```\n{error}\n```")
    await errorCh.send(embed=embed)

    if message != None:
        embed = discord.Embed(title="오류 발생!",
                              description="명령어를 실행하는 동안 오류가 발생하였습니다.\n조금 뒤에 다시 시도해 주세요.\n오류가 지속된다면, 저에게 DM으로 지원 메시지를 보내주시길 바랍니다.",
                              color=red, timestamp=dt.utcnow())
        await message.channel.send(embed=embed)

def tierCompare(solorank,flexrank):
    if tierScore[solorank] > tierScore[flexrank]:
        return 0
    elif tierScore[solorank] < tierScore[flexrank]:
        return 1
    else:
        return 2

def deleteTags(htmls):
    for a in range(len(htmls)):
        htmls[a] = re.sub('<.+?>','',str(htmls[a]),0).strip()
    return htmls

#Strip accents in english : Like a in jäger
def convertToNormalEnglish(text):
    return ''.join(char for char in unicodedata.normalize('NFKD', text) if unicodedata.category(char) != 'Mn')

def deleteTags(htmls):
    for a in range(len(htmls)):
        htmls[a] = re.sub('<.+?>','',str(htmls[a]),0).strip()
    return htmls

@client.event # Use these decorator to register an event.
async def on_ready(): # on_ready() event : when the bot has finised logging in and setting things up
    await client.change_presence(status=discord.Status.online, activity=discord.Game("!help 혹은 !도움말 로 도움을 받으실 수 있습니다!"))
    print("New log in as {0.user}".format(client))

@client.event
async def on_message(message): # on_message() event : when the bot has recieved a message
    #To user who sent message
    # await message.author.send(msg)
    print(message.content)
    if message.author == client.user:
        return

@client.event
async def on_message(message): # on_message() event : when the bot has recieved a message
    if message.content.startswith("!ㅎㅇ"):
        await message.channel.send("안녕하세요 :D")
    if message.content.startswith("!안녕"):
        await message.channel.send("안녕하세요 :ㅇ")
        #To user who sent message
    # await message.author.send(msg)
    print(message.content)
    if message.author == client.user:
        return

    command = message.content[1:].split()[0]
    commandLine = []
    if len(message.content.split()) > 1: commandLine = message.content.split()[1:]

    if message.content.startswith("!핑"):
        msg = await message.channel.send(embed=discord.Embed(title=":ping_pong: 퐁!",
                                                             description=f"현재 WH3N_BOT 은 ``{int(client.latency * 1000)}ms``의 지연시간을 가지고 있습니다.",
                                                             color=blue, timestamp=datetime.datetime.utcnow()))
        ping = int((datetime.datetime.utcnow() - msg.created_at).total_seconds() * 1000)
        await msg.edit(embed=discord.Embed(title=":ping_pong: 퐁!",
                                           description=f"현재 WH3N_BOT 은 ``{int(client.latency * 1000)}ms``의 지연시간을 가지고 있습니다.\n저와 {message.author.display_name}님이 닿기까지는 ``{ping}ms``가 걸렸습니다.",
                                           color=blue, timestamp=datetime.datetime.utcnow()))

    if message.content.startswith("!도움말"):
        channel = message.channel
        embed = discord.Embed(
            title = '도움말',
            description = '각각의 명령어들 입니다. 본 명령어를 치시면 항상 보실수 있어요 :ㅇ  (닉네임에 뛰어쓰기가 있으시면 -로 구분하시면 됩니다.)',
            colour = discord.Colour.blue()
        )

        #embed.set_footer(text = '끗')
        dtime = datetime.datetime.now()
        #print(dtime[0:4]) # 년도
        #print(dtime[5:7]) #월
        #print(dtime[8:11])#일
        #print(dtime[11:13])#시
        #print(dtime[14:16])#분
        #print(dtime[17:19])#초
        embed.set_footer(text=str(dtime.year)+"년 "+str(dtime.month)+"월 "+str(dtime.day)+"일 "+str(dtime.hour)+"시 "+str(dtime.minute)+"분 "+str(dtime.second)+"초")
        #embed.set_footer(text=dtime[0:4]+"년 "+dtime[5:7]+"월 "+dtime[8:11]+"일 "+dtime[11:13]+"시 "+dtime[14:16]+"분 "+dtime[17:19]+"초")
        embed.add_field(name='!도움말', value='본 내용을 보여드립니다', inline=False)
        embed.add_field(name='!ㅎㅇ / !안녕', value='인사를 해드립니다 :D', inline=False)
        embed.add_field(name='!주사위', value='1부터 6사이의 숫자가 랜덤으로 나옵니다', inline=False)
        embed.add_field(name='!배그경쟁1 (닉네임)', value='TPP(3인칭)의 배틀그라운드 경쟁 전적을 보여드립니다', inline=False)
        embed.add_field(name='!배그경쟁2 (닉네임)', value='FPP(1인칭)의 배틀그라운드 일반 전적을 보여드립니다', inline=False)
        embed.add_field(name='!배그솔로1 (닉네임)', value='TPP(3인칭)의 배틀그라운드 일반 전적을 보여드립니다', inline=False)
        embed.add_field(name='!배그솔로2 (닉네임)', value='FPP(1인칭)의 배틀그라운드 일반 전적을 보여드립니다', inline=False)
        embed.add_field(name='!배그듀오1 (닉네임)', value='TPP(3인칭)의 배틀그라운드 일반 듀오 전적을 보여드립니다', inline=False)
        embed.add_field(name='!배그듀오2 (닉네임)', value='FPP(1인칭)의 배틀그라운드 일반 듀오 전적을 보여드립니다', inline=False)
        embed.add_field(name='!배그스쿼드1 (닉네임)', value='TPP(3인칭)의 배틀그라운드 일반 스쿼드 전적을 보여드립니다', inline=False)
        embed.add_field(name='!배그스쿼드2 (닉네임)', value='FPP(1인칭)의 배틀그라운드 일반 스쿼드 전적을 보여드립니다', inline=False)
        #embed.add_field(name='!레식전적 (닉네임)', value='레인보우식스 시즈의 랭크 정보와 레벨, 티어등을 보여드립니다', inline=False)
        #embed.add_field(name='!레식오퍼 (닉네임)', value='레인보우식스 시즈의 오퍼레이터 정보(킬 ,데스,승률,가장 많이 플레이한 오퍼 순위)를 보여드립니다', inline=False)
        embed.add_field(name='!롤전적 (닉네임)', value='롤의 플레이어 정보(전적)을 보여드립니다', inline=False)
        embed.add_field(name='!핑', value='봇의 핑 정보를 보여드립니다.', inline=False)
        #embed.add_field(name='!마스크판매 (지역명)', value='마스크를 100개 이상 보유중인 약국들의 마스크 판매 현황을 보여드립니다.', inline=False)

        await message.channel.send(embed=embed)

    if message.content.startswith("!도움말"):
        await message.channel.send("봇의 도움말입니다 '~' 잘 부탁드려요!")

    if message.content.startswith("!help"):
        channel = message.channel
        embed = discord.Embed(
            title = '도움말',
            description = '각각의 명령어들 입니다. 본 명령어를 치시면 항상 보실수 있어요     :ㅇ  (닉네임에 뛰어쓰기가 있으시다면 -로 구분하시면 됩니다!)',
            colour = discord.Colour.blue()
        )

        #embed.set_footer(text = '끗')
        dtime = datetime.datetime.now()
        #print(dtime[0:4]) # 년도
        #print(dtime[5:7]) #월
        #print(dtime[8:11])#일
        #print(dtime[11:13])#시
        #print(dtime[14:16])#분
        #print(dtime[17:19])#초
        embed.set_footer(text=str(dtime.year)+"년 "+str(dtime.month)+"월 "+str(dtime.day)+"일 "+str(dtime.hour)+"시 "+str(dtime.minute)+"분 "+str(dtime.second)+"초")
        #embed.set_footer(text=dtime[0:4]+"년 "+dtime[5:7]+"월 "+dtime[8:11]+"일 "+dtime[11:13]+"시 "+dtime[14:16]+"분 "+dtime[17:19]+"초")
        embed.add_field(name='!도움말 / !help', value='본 내용을 보여드립니다', inline=False)
        embed.add_field(name='!ㅎㅇ / !안녕', value='인사를 해드립니다 :D', inline=False)
        embed.add_field(name='!주사위', value='1부터 6사이의 숫자가 랜덤으로 나옵니다', inline=False)
        embed.add_field(name='!배그경쟁1 (닉네임)', value='TPP(3인칭)의 배틀그라운드 경쟁 전적을 보여드립니다', inline=False)
        embed.add_field(name='!배그경쟁2 (닉네임)', value='FPP(1인칭)의 배틀그라운드 일반 전적을 보여드립니다', inline=False)
        embed.add_field(name='!배그솔로1 (닉네임)', value='TPP(3인칭)의 배틀그라운드 일반 전적을 보여드립니다', inline=False)
        embed.add_field(name='!배그솔로2 (닉네임)', value='FPP(1인칭)의 배틀그라운드 일반 전적을 보여드립니다', inline=False)
        embed.add_field(name='!배그듀오1 (닉네임)', value='TPP(3인칭)의 배틀그라운드 일반 듀오 전적을 보여드립니다', inline=False)
        embed.add_field(name='!배그듀오2 (닉네임)', value='FPP(1인칭)의 배틀그라운드 일반 듀오 전적을 보여드립니다', inline=False)
        embed.add_field(name='!배그스쿼드1 (닉네임)', value='TPP(3인칭)의 배틀그라운드 일반 스쿼드 전적을 보여드립니다', inline=False)
        embed.add_field(name='!배그스쿼드2 (닉네임)', value='FPP(1인칭)의 배틀그라운드 일반 스쿼드 전적을 보여드립니다', inline=False)
        #embed.add_field(name='!레식전적 (닉네임)', value='레인보우식스 시즈의 랭크 정보와 레벨, 티어등을 보여드립니다', inline=False)
        #embed.add_field(name='!레식오퍼 (닉네임)', value='레인보우식스 시즈의 오퍼레이터 정보(킬 ,데스,승률,가장 많이 플레이한 오퍼 순위)를 보여드립니다', inline=False)
        embed.add_field(name='!롤전적 (닉네임)', value='롤의 플레이어 정보(전적)을 보여드립니다', inline=False)
        #embed.add_field(name='!마스크판매 (지역명)', value='마스크를 100개 이상 보유중인 약국들의 마스크 판매 현황을 보여드립니다.', inline=False)
        
        await message.channel.send(embed=embed)

    if message.content.startswith("!help"):
        await message.channel.send("봇의 도움말입니다 '~' 잘 부탁드려요!")

    if message.content.startswith('!주사위'):

        random_num = random.randrange(1, 7)  # 1~6까지 랜덤수
        print(random_num)
        if random_num == 1:
            await message.channel.send(embed=discord.Embed(description=':game_die: ' + ':one:'))
        if random_num == 2:
            await message.channel.send(embed=discord.Embed(description=':game_die: ' + ':two:'))
        if random_num == 3:
            await message.channel.send(embed=discord.Embed(description=':game_die: ' + ':three:'))
        if random_num == 4:
            await message.channel.send(embed=discord.Embed(description=':game_die: ' + ':four:'))
        if random_num == 5:
            await message.channel.send(embed=discord.Embed(description=':game_die: ' + ':five:'))
        if random_num == 6:
            await message.channel.send(embed=discord.Embed(description=':game_die: ' + ':six: '))

    if message.content.startswith("!배그경쟁1"):  # TabErrorTPP
        baseURL = "https://dak.gg/profile/"
        playerNickname = ''.join((message.content).split(' ')[1:])
        URL = baseURL + quote(playerNickname)

        try:
            html = urlopen(URL)
            bs = BeautifulSoup(html, 'html.parser')
            if len(message.content.split(" ")) == 1:
                embed = discord.Embed(title="닉네임이 입력되지 않았습니다", description="", color=0x5CD1E5)
                embed.add_field(name="Player nickname not entered",
                                value="To use command !경쟁전(1 : TPP or 2 : FPP) : !경쟁전 (Nickname)", inline=False)
                embed.set_footer(text='Service provided by WH3N_GG#7758.')
                await message.channel.send("Error : Incorrect command usage ", embed=embed)
            else:
                accessors = bs.findAll('a', {'href': re.compile('\/statistics\/[A-Za-z]')})

                # Season Information : ['PUBG',(season info),(Server),'overview']
                seasonInfo = []
                for si in bs.findAll('li', {'class': "active"}):
                    seasonInfo.append(si.text.strip())
                serverAccessorAndStatus = []
                # To prevent : Parsing Server Status, Make a result like Server:\nOnline. So I need to delete '\n'to get good result
                for a in accessors:
                    serverAccessorAndStatus.append(re.sub(pattern='[\n]', repl="", string=a.text.strip()))

                # Varaible serverAccessorAndStatus : [(accessors),(ServerStatus),(Don't needed value)]

                # Varaibel rankElements : index 0: fpp 1 : tpp

                rankElements = bs.findAll('div', {'class': re.compile('squad ranked [A-Za-z0-9]')})

                '''
                -> 클래스 값을 가져와서 판별하는 것도 있지만 이 방법을 사용해 본다.
                -> 만약 기록이 존재 하지 않는 경우 class 가 no_record라는 값을 가진 <div>가 생성된다. 이 태그로 데이터 유무 판별하면된다.
                print(rankElements[1].find('div',{'class' : 'no_record'}))
                '''

                if rankElements[0].find('div',
                                        {'class': 'no_record'}) != None:  # 인덱스 0 : 경쟁전 fpp -> 정보가 있는지 없는지 유무를 판별한다.
                    embed = discord.Embed(title="Record not found", description="Rank TPP record not found.",
                                          color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    embed.set_footer(text='Service provided by WH3N_GG#7758.')
                    await message.channel.send("PUBG player " + playerNickname + "'s TPP Ranking information",
                                               embed=embed)
                else:
                    # Short of fpp Rank
                    fR = rankElements[0]
                    # Tier Information

                    # Get tier medal image
                    tierMedalImage = fR.find('div', {'class': 'grade-info'}).img['src']
                    # Get tier Information
                    tierInfo = fR.find('div', {'class': 'grade-info'}).img['alt']

                    # Rating Inforamtion
                    # RP Score
                    RPScore = fR.find('div', {'class': 'rating'}).find('span', {'class': 'caption'}).text

                    # Get top rate statistics

                    # 등수
                    topRatioRank = topRatio = fR.find('p', {'class': 'desc'}).find('span', {'class': 'rank'}).text
                    # 상위 %
                    topRatio = fR.find('p', {'class': 'desc'}).find('span', {'class': 'top'}).text

                    # Main : Stats all in here.

                    mainStatsLayout = fR.find('div', {'class': 'stats'})

                    # Stats Data Saved As List

                    statsList = mainStatsLayout.findAll('p', {'class': 'value'})  # [KDA,승률,Top10,평균딜량, 게임수, 평균등수]
                    statsRatingList = mainStatsLayout.findAll('span', {'class': 'top'})  # [KDA, 승률,Top10 평균딜량, 게임수]

                    for r in range(0, len(statsList)):
                        # \n으로 큰 여백이 있어 split 처리
                        statsList[r] = statsList[r].text.strip().split('\n')[0]
                        statsRatingList[r] = statsRatingList[r].text
                    # 평균등수는 stats Rating을 표시하지 않는다.
                    statsRatingList = statsRatingList[0:5]

                    embed = discord.Embed(title="Player Unkonw Battle Ground player search from dak.gg", description="",
                                          color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    embed.add_field(name="Real Time Accessors and Server Status",
                                    value="Accessors : " + serverAccessorAndStatus[0] + " | " "Server Status : " +
                                          serverAccessorAndStatus[1].split(':')[-1], inline=False)
                    embed.add_field(name="Player located server", value=seasonInfo[2] + " Server", inline=False)
                    embed.add_field(name="티어 / 최대 티어 / 평균 티어",
                                    value=tierInfo + " (" + RPScore + ") / " + topRatio + " / " + topRatioRank,
                                    inline=False)
                    embed.add_field(name="K/D", value=statsList[0] + "/" + statsRatingList[0], inline=True)
                    embed.add_field(name="승률", value=statsList[1] + "/" + statsRatingList[1], inline=True)
                    embed.add_field(name="Top 10 비율", value=statsList[2] + "/" + statsRatingList[2], inline=True)
                    embed.add_field(name="평균딜량", value=statsList[3] + "/" + statsRatingList[3], inline=True)
                    embed.add_field(name="게임수", value=statsList[4] + "판/" + statsRatingList[4], inline=True)
                    embed.add_field(name="평균등수", value=statsList[5], inline=True)
                    embed.set_footer(text='Service provided by WH3N_GG#7758.')
                    await message.channel.send("PUBG player " + playerNickname + "'s TPP Ranking information",
                                               embed=embed)


        except HTTPError as e:
            embed = discord.Embed(title="Not existing plyer",
                                  description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",
                                  color=0x5CD1E5)
            await message.channel.send("Error : Not existing player", embed=embed)
            print(e)
        except AttributeError as e:
            embed = discord.Embed(title="Not existing plyer",
                                  description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",
                                  color=0x5CD1E5)
            await message.channel.send("Error : Not existing player", embed=embed)
            print(e)

    if message.content.startswith("!배그경쟁2"):  # FPP
        baseURL = "https://dak.gg/profile/"
        playerNickname = ''.join((message.content).split(' ')[1:])
        URL = baseURL + quote(playerNickname)

        try:
            html = urlopen(URL)
            bs = BeautifulSoup(html, 'html.parser')
            if len(message.content.split(" ")) == 1:
                embed = discord.Embed(title="닉네임이 입력되지 않았습니다", description="", color=0x5CD1E5)
                embed.add_field(name="Player nickname not entered",
                                value="To use command !경쟁전(1 : TPP or 2 : FPP) : !경쟁전 (Nickname)", inline=False)
                embed.set_footer(text='Service provided by WH3N_GG#7758.')
                await message.channel.send("Error : Incorrect command usage ", embed=embed)
            else:
                accessors = bs.findAll('a', {'href': re.compile('\/statistics\/[A-Za-z]')})

                # Season Information : ['PUBG',(season info),(Server),'overview']
                seasonInfo = []
                for si in bs.findAll('li', {'class': "active"}):
                    seasonInfo.append(si.text.strip())
                serverAccessorAndStatus = []
                # To prevent : Parsing Server Status, Make a result like Server:\nOnline. So I need to delete '\n'to get good result
                for a in accessors:
                    serverAccessorAndStatus.append(re.sub(pattern='[\n]', repl="", string=a.text.strip()))

                # Varaible serverAccessorAndStatus : [(accessors),(ServerStatus),(Don't needed value)]

                # index 0: fpp 1 : tpp

                rankElements = bs.findAll('div', {'class': re.compile('squad ranked [A-Za-z0-9]')})

                '''
                -> 클래스 값을 가져와서 판별하는 것도 있지만 이 방법을 사용해 본다.
                -> 만약 기록이 존재 하지 않는 경우 class 가 no_record라는 값을 가진 <div>가 생성된다. 이 태그로 데이터 유무 판별하면된다.
                print(rankElements[1].find('div',{'class' : 'no_record'}))
                '''

                if rankElements[1].find('div',
                                        {'class': 'no_record'}) != None:  # 인덱스 0 : 경쟁전 fpp -> 정보가 있는지 없는지 유무를 판별한다a.
                    embed = discord.Embed(title="Record not found", description="Solo que record not found.",
                                          color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    embed.set_footer(text='Service provided by WH3N_GG#7758.')
                    await message.channel.send("PUBG player " + playerNickname + "'s FPP Ranking information",
                                               embed=embed)
                else:
                    # Short of fpp Rank
                    fR = rankElements[1]
                    # Tier Information

                    # Get tier medal image
                    tierMedalImage = fR.find('div', {'class': 'grade-info'}).img['src']
                    # Get tier Information
                    tierInfo = fR.find('div', {'class': 'grade-info'}).img['alt']

                    # Rating Inforamtion
                    # RP Score
                    RPScore = fR.find('div', {'class': 'rating'}).find('span', {'class': 'caption'}).text

                    # Get top rate statistics

                    # 등수
                    topRatioRank = topRatio = fR.find('p', {'class': 'desc'}).find('span', {'class': 'rank'}).text
                    # 상위 %
                    topRatio = fR.find('p', {'class': 'desc'}).find('span', {'class': 'top'}).text

                    # Main : Stats all in here.

                    mainStatsLayout = fR.find('div', {'class': 'stats'})

                    # Stats Data Saved As List

                    statsList = mainStatsLayout.findAll('p', {'class': 'value'})  # [KDA,승률,Top10,평균딜량, 게임수, 평균등수]
                    statsRatingList = mainStatsLayout.findAll('span', {'class': 'top'})  # [KDA, 승률,Top10 평균딜량, 게임수]

                    for r in range(0, len(statsList)):
                        # \n으로 큰 여백이 있어 split 처리
                        statsList[r] = statsList[r].text.strip().split('\n')[0]
                        statsRatingList[r] = statsRatingList[r].text
                    # 평균등수는 stats Rating을 표시하지 않는다.
                    statsRatingList = statsRatingList[0:5]

                    embed = discord.Embed(title="Player Unkonw Battle Ground player search from dak.gg", description="",
                                          color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    embed.add_field(name="Real Time Accessors and Server Status",
                                    value="Accessors : " + serverAccessorAndStatus[0] + " | " "Server Status : " +
                                          serverAccessorAndStatus[1].split(':')[-1], inline=False)
                    embed.add_field(name="Player located server", value=seasonInfo[2] + " Server", inline=False)
                    embed.add_field(name="티어 / 최대 티어 / 평균 티어",
                                    value=tierInfo + " (" + RPScore + ") / " + topRatio + " / " + topRatioRank,
                                    inline=False)
                    embed.add_field(name="K/D", value=statsList[0] + "/" + statsRatingList[0], inline=True)
                    embed.add_field(name="승률", value=statsList[1] + "/" + statsRatingList[1], inline=True)
                    embed.add_field(name="Top 10 비율", value=statsList[2] + "/" + statsRatingList[2], inline=True)
                    embed.add_field(name="평균딜량", value=statsList[3] + "/" + statsRatingList[3], inline=True)
                    embed.add_field(name="게임수", value=statsList[4] + "판/" + statsRatingList[4], inline=True)
                    embed.add_field(name="평균등수", value=statsList[5], inline=True)
                    embed.set_footer(text='Service provided by WH3N_GG#7758.')
                    await message.channel.send("PUBG player " + playerNickname + "'s FPP Ranking information",
                                               embed=embed)


        except HTTPError as e:
            embed = discord.Embed(title="Not existing plyer",
                                  description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",
                                  color=0x5CD1E5)
            await message.channel.send("Error : Not existing player", embed=embed)
        except AttributeError as e:
            embed = discord.Embed(title="Not existing plyer",
                                  description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",
                                  color=0x5CD1E5)
            await message.channel.send("Error : Not existing player", embed=embed)

    if message.content.startswith("!배그솔로1"):
        baseURL = "https://dak.gg/profile/"
        playerNickname = ''.join((message.content).split(' ')[1:])
        URL = baseURL + quote(playerNickname)
        try:
            html = urlopen(URL)
            bs = BeautifulSoup(html, 'html.parser')
            if len(message.content.split(" ")) == 1:
                embed = discord.Embed(title="닉네임이 입력되지 않았습니다", description="", color=0x5CD1E5)
                embed.add_field(name="Player nickname not entered",
                                value="To use command !배그솔로 : !배그솔로 (Nickname)", inline=False)
                embed.set_footer(text='Service provided by WH3N_GG#7758.')
                await message.channel.send("Error : Incorrect command usage ", embed=embed)

            else:
                accessors = bs.findAll('a', {'href': re.compile('\/statistics\/[A-Za-z]')})

                # Season Information : ['PUBG',(season info),(Server),'overview']
                seasonInfo = []
                for si in bs.findAll('li', {'class': "active"}):
                    seasonInfo.append(si.text.strip())
                serverAccessorAndStatus = []
                # To prevent : Parsing Server Status, Make a result like Server:\nOnline. So I need to delete '\n'to get good result
                for a in accessors:
                    serverAccessorAndStatus.append(re.sub(pattern='[\n]', repl="", string=a.text.strip()))

                # Varaible serverAccessorAndStatus : [(accessors),(ServerStatus),(Don't needed value)]

                soloQueInfo = bs.find('section', {'class': "solo modeItem"}).find('div', {'class': "mode-section tpp"})
                if soloQueInfo == None:
                    embed = discord.Embed(title="플레이 내역이 존재하지 않습니다", description="솔로 플레이 내역이 존재하지 않습니다.",
                                          color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    await message.channel.send("PUBG player " + playerNickname + "'s TPP solo que information",
                                               embed=embed)
                else:
                    # print(soloQueInfo)
                    # Get total playtime
                    soloQueTotalPlayTime = soloQueInfo.find('span', {'class': "time_played"}).text.strip()
                    # Get Win/Top10/Lose : [win,top10,lose]
                    soloQueGameWL = soloQueInfo.find('em').text.strip().split(' ')
                    # RankPoint
                    rankPoint = soloQueInfo.find('span', {'class': 'value'}).text
                    # Tier image url, tier
                    tierInfos = soloQueInfo.find('img', {
                        'src': re.compile('\/\/static\.dak\.gg\/images\/icons\/tier\/[A-Za-z0-9_.]')})
                    tierImage = "https:" + tierInfos['src']
                    print(tierImage)
                    tier = tierInfos['alt']

                    # Comprehensive info
                    comInfo = []
                    # [K/D,승률,Top10,평균딜량,게임수, 최다킬수,헤드샷,저격거리,생존,평균순위]
                    for ci in soloQueInfo.findAll('p', {'class': 'value'}):
                        comInfo.append(ci.text.strip())
                    comInfopercentage = []
                    # [전체 상위 %, K/D,승률,Top10,평균딜량,게임수,최다킬수,헤드샷,저격,생존,None]
                    for cif in soloQueInfo.findAll('span', {'class': 'top'}):
                        comInfopercentage.append((cif.text))

                    embed = discord.Embed(title="Player Unkonw Battle Ground player search from dak.gg", description="",
                                          color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    embed.add_field(name="Real Time Accessors and Server Status",
                                    value="Accessors : " + serverAccessorAndStatus[0] + " | " "Server Status : " +
                                          serverAccessorAndStatus[1].split(':')[-1], inline=False)
                    embed.add_field(name="사용자 서버 / 플레이 시간",
                                    value=seasonInfo[2] + " Server / Total playtime : " + soloQueTotalPlayTime,
                                    inline=False)
                    embed.add_field(name="티어 / 최대 티어 / 평균 티어",
                                    value=tier + " (" + rankPoint + "p)" + " / " + comInfopercentage[0] + " / " +
                                          comInfo[-1], inline=False)
                    embed.add_field(name="K/D", value=comInfo[0] + "/" + comInfopercentage[1], inline=True)
                    embed.add_field(name="승률", value=comInfo[1] + "/" + comInfopercentage[2], inline=True)
                    embed.add_field(name="Top 10 비율", value=comInfo[2] + "/" + comInfopercentage[3], inline=True)
                    embed.add_field(name="평균딜량", value=comInfo[3] + "/" + comInfopercentage[4], inline=True)
                    embed.add_field(name="게임수", value=comInfo[4] + "판/" + comInfopercentage[5], inline=True)
                    embed.add_field(name="최다킬수", value=comInfo[5] + "킬/" + comInfopercentage[6], inline=True)
                    embed.add_field(name="헤드샷 비율", value=comInfo[6] + "/" + comInfopercentage[7], inline=True)
                    embed.add_field(name="저격거리", value=comInfo[7] + "/" + comInfopercentage[8], inline=True)
                    embed.add_field(name="평균생존시간", value=comInfo[8] + "/" + comInfopercentage[9], inline=True)
                    embed.set_thumbnail(url=tierImage)
                    embed.set_footer(text='Service provided by WH3N_GG#7758.')
                    await message.channel.send("PUBG player " + playerNickname + "'s TPP solo que information",
                                               embed=embed)
        except HTTPError as e:
            embed = discord.Embed(title="Not existing plyer",
                                  description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",
                                  color=0x5CD1E5)
            await message.channel.send("Error : Not existing player", embed=embed)
        except AttributeError as e:
            embed = discord.Embed(title="Not existing plyer",
                                  description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",
                                  color=0x5CD1E5)
            await message.channel.send("Error : Not existing player", embed=embed)

    if message.content.startswith("!배그듀오1"):
        baseURL = "https://dak.gg/profile/"
        playerNickname = ''.join((message.content).split(' ')[1:])
        URL = baseURL + quote(playerNickname)
        try:
            html = urlopen(URL)
            bs = BeautifulSoup(html, 'html.parser')
            if len(message.content.split(" ")) == 1:
                embed = discord.Embed(title="닉네임이 입력되지 않았습니다", description="", color=0x5CD1E5)
                embed.add_field(name="Player nickname not entered",
                                value="To use command !배그스쿼드 : !배그스쿼드 (Nickname)", inline=False)
                embed.set_footer(text='Service provided by WH3N_GG#7758.')
                await message.channel.send("Error : Incorrect command usage ", embed=embed)

            else:
                accessors = bs.findAll('a', {'href': re.compile('\/statistics\/[A-Za-z]')})

                # Season Information : ['PUBG',(season info),(Server),'overview']
                seasonInfo = []
                for si in bs.findAll('li', {'class': "active"}):
                    seasonInfo.append(si.text.strip())
                serverAccessorAndStatus = []
                # To prevent : Parsing Server Status, Make a result like Server:\nOnline. So I need to delete '\n'to get good result
                for a in accessors:
                    serverAccessorAndStatus.append(re.sub(pattern='[\n]', repl="", string=a.text.strip()))

                # Varaible serverAccessorAndStatus : [(accessors),(ServerStatus),(Don't needed value)]

                duoQueInfo = bs.find('section', {'class': "duo modeItem"}).find('div', {'class': "mode-section tpp"})
                if duoQueInfo == None:
                    embed = discord.Embed(title="", description="듀오 플레이 기록이 존재하지 않습니다.",
                                          color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    await message.channel.send("PUBG player " + playerNickname + "'s TPP duo que information",
                                               embed=embed)
                else:
                    # print(duoQueInfo)
                    # Get total playtime
                    duoQueTotalPlayTime = duoQueInfo.find('span', {'class': "time_played"}).text.strip()
                    # Get Win/Top10/Lose : [win,top10,lose]
                    duoQueGameWL = duoQueInfo.find('em').text.strip().split(' ')
                    # RankPoint
                    rankPoint = duoQueInfo.find('span', {'class': 'value'}).text
                    # Tier image url, tier
                    tierInfos = duoQueInfo.find('img', {
                        'src': re.compile('\/\/static\.dak\.gg\/images\/icons\/tier\/[A-Za-z0-9_.]')})
                    tierImage = "https:" + tierInfos['src']
                    tier = tierInfos['alt']

                    # Comprehensive info
                    comInfo = []
                    # [K/D,승률,Top10,평균딜량,게임수, 최다킬수,헤드샷,저격거리,생존,평균순위]
                    for ci in duoQueInfo.findAll('p', {'class': 'value'}):
                        comInfo.append(ci.text.strip())
                    comInfopercentage = []
                    # [전체 상위 %, K/D,승률,Top10,평균딜량,게임수,최다킬수,헤드샷,저격,생존,None]
                    for cif in duoQueInfo.findAll('span', {'class': 'top'}):
                        comInfopercentage.append((cif.text))

                    embed = discord.Embed(title="Player Unkonw Battle Ground player search from dak.gg", description="",
                                          color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    embed.add_field(name="Real Time Accessors and Server Status",
                                    value="Accessors : " + serverAccessorAndStatus[0] + " | " "Server Status : " +
                                          serverAccessorAndStatus[1].split(':')[-1], inline=False)
                    embed.add_field(name="사용자 서버 / 플레이 시간",
                                    value=seasonInfo[2] + " Server / Total playtime : " + duoQueTotalPlayTime,
                                    inline=False)
                    embed.add_field(name="티어 / 최대 티어 / 평균 티어",
                                    value=tier + " (" + rankPoint + "p)" + " / " + comInfopercentage[0] + " / " +
                                          comInfo[-1], inline=False)
                    embed.add_field(name="K/D", value=comInfo[0] + "/" + comInfopercentage[1], inline=True)
                    embed.add_field(name="승률", value=comInfo[1] + "/" + comInfopercentage[2], inline=True)
                    embed.add_field(name="Top 10 비율", value=comInfo[2] + "/" + comInfopercentage[3], inline=True)
                    embed.add_field(name="평균딜량", value=comInfo[3] + "/" + comInfopercentage[4], inline=True)
                    embed.add_field(name="게임수", value=comInfo[4] + "판/" + comInfopercentage[5], inline=True)
                    embed.add_field(name="최다킬수", value=comInfo[5] + "킬/" + comInfopercentage[6], inline=True)
                    embed.add_field(name="헤드샷 비율", value=comInfo[6] + "/" + comInfopercentage[7], inline=True)
                    embed.add_field(name="저격거리", value=comInfo[7] + "/" + comInfopercentage[8], inline=True)
                    embed.add_field(name="평균생존시간", value=comInfo[8] + "/" + comInfopercentage[9], inline=True)
                    embed.set_thumbnail(url=tierImage)
                    embed.set_footer(text='Service provided by WH3N_GG#7758.')
                    await message.channel.send("PUBG player " + playerNickname + "'s TPP duo que information",
                                               embed=embed)
        except HTTPError as e:
            embed = discord.Embed(title="Not existing plyer",
                                  description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",
                                  color=0x5CD1E5)
            await message.channel.send("Error : Not existing player", embed=embed)
        except AttributeError as e:
            embed = discord.Embed(title="Not existing plyer",
                                  description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",
                                  color=0x5CD1E5)
            await message.channel.send("Error : Not existing player", embed=embed)

    if message.content.startswith("!배그스쿼드1"):
        baseURL = "https://dak.gg/profile/"
        playerNickname = ''.join((message.content).split(' ')[1:])
        URL = baseURL + quote(playerNickname)
        try:
            html = urlopen(URL)
            bs = BeautifulSoup(html, 'html.parser')
            if len(message.content.split(" ")) == 1:
                embed = discord.Embed(title="닉네임이 입력되지 않았습니다", description="", color=0x5CD1E5)
                embed.add_field(name="Player nickname not entered",
                                value="To use command !배그솔로 : !배그솔로 (Nickname)", inline=False)
                embed.set_footer(text='Service provided by WH3N_GG#7758.')
                await message.channel.send("Error : Incorrect command usage ", embed=embed)

            else:
                accessors = bs.findAll('a', {'href': re.compile('\/statistics\/[A-Za-z]')})

                # Season Information : ['PUBG',(season info),(Server),'overview']
                seasonInfo = []
                for si in bs.findAll('li', {'class': "active"}):
                    seasonInfo.append(si.text.strip())
                serverAccessorAndStatus = []
                # To prevent : Parsing Server Status, Make a result like Server:\nOnline. So I need to delete '\n'to get good result
                for a in accessors:
                    serverAccessorAndStatus.append(re.sub(pattern='[\n]', repl="", string=a.text.strip()))

                # Varaible serverAccessorAndStatus : [(accessors),(ServerStatus),(Don't needed value)]

                squadQueInfo = bs.find('section', {'class': "squad modeItem"}).find('div',
                                                                                    {'class': "mode-section tpp"})
                if squadQueInfo == None:
                    embed = discord.Embed(title="플레이 내역이 존재하지 않습니다", description="스쿼드 플레이 내역이 존재하지 않습니다.",
                                          color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    await message.channel.send("PUBG player " + playerNickname + "'s TPP squad que information",
                                               embed=embed)
                else:
                    # print(duoQueInfo)
                    # Get total playtime
                    squadQueTotalPlayTime = squadQueInfo.find('span', {'class': "time_played"}).text.strip()
                    # Get Win/Top10/Lose : [win,top10,lose]
                    squadQueGameWL = squadQueInfo.find('em').text.strip().split(' ')
                    # RankPoint
                    rankPoint = squadQueInfo.find('span', {'class': 'value'}).text
                    # Tier image url, tier
                    tierInfos = squadQueInfo.find('img', {
                        'src': re.compile('\/\/static\.dak\.gg\/images\/icons\/tier\/[A-Za-z0-9_.]')})
                    tierImage = "https:" + tierInfos['src']
                    tier = tierInfos['alt']

                    # Comprehensive info
                    comInfo = []
                    # [K/D,승률,Top10,평균딜량,게임수, 최다킬수,헤드샷,저격거리,생존,평균순위]
                    for ci in squadQueInfo.findAll('p', {'class': 'value'}):
                        comInfo.append(ci.text.strip())
                    comInfopercentage = []
                    # [전체 상위 %, K/D,승률,Top10,평균딜량,게임수,최다킬수,헤드샷,저격,생존,None]
                    for cif in squadQueInfo.findAll('span', {'class': 'top'}):
                        comInfopercentage.append((cif.text))

                    embed = discord.Embed(title="Player Unkonw Battle Ground player search from dak.gg", description="",
                                          color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    embed.add_field(name="Real Time Accessors and Server Status",
                                    value="Accessors : " + serverAccessorAndStatus[0] + " | " "Server Status : " +
                                          serverAccessorAndStatus[1].split(':')[-1], inline=False)
                    embed.add_field(name="사용자 서버",
                                    value=seasonInfo[2] + " Server / Total playtime : " + squadQueTotalPlayTime,
                                    inline=False)
                    embed.add_field(name="티어 / 최대 티어 / 평균 티어",
                                    value=tier + " (" + rankPoint + "p)" + " / " + comInfopercentage[0] + " / " +
                                          comInfo[-1], inline=False)
                    embed.add_field(name="K/D", value=comInfo[0] + "/" + comInfopercentage[1], inline=True)
                    embed.add_field(name="승률", value=comInfo[1] + "/" + comInfopercentage[2], inline=True)
                    embed.add_field(name="Top 10 비율", value=comInfo[2] + "/" + comInfopercentage[3], inline=True)
                    embed.add_field(name="평균딜량", value=comInfo[3] + "/" + comInfopercentage[4], inline=True)
                    embed.add_field(name="게임수", value=comInfo[4] + "판/" + comInfopercentage[5], inline=True)
                    embed.add_field(name="최다킬수", value=comInfo[5] + "킬/" + comInfopercentage[6], inline=True)
                    embed.add_field(name="헤드샷 비율", value=comInfo[6] + "/" + comInfopercentage[7], inline=True)
                    embed.add_field(name="저격거리", value=comInfo[7] + "/" + comInfopercentage[8], inline=True)
                    embed.add_field(name="평균생존시간", value=comInfo[8] + "/" + comInfopercentage[9], inline=True)
                    embed.set_thumbnail(url=tierImage)
                    embed.set_footer(text='Service provided by WH3N_GG#7758.')
                    await message.channel.send("PUBG player " + playerNickname + "'s TPP squad que information",
                                               embed=embed)
        except HTTPError as e:
            embed = discord.Embed(title="Not existing plyer",
                                  description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",
                                  color=0x5CD1E5)
            await message.channel.send("Error : Not existing player", embed=embed)
        except AttributeError as e:
            embed = discord.Embed(title="Not existing plyer",
                                  description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",
                                  color=0x5CD1E5)
            await message.channel.send("Error : Not existing player", embed=embed)

    if message.content.startswith("!배그솔로2"):
        baseURL = "https://dak.gg/profile/"
        playerNickname = ''.join((message.content).split(' ')[1:])
        URL = baseURL + quote(playerNickname)
        try:
            html = urlopen(URL)
            bs = BeautifulSoup(html, 'html.parser')
            if len(message.content.split(" ")) == 1:
                embed = discord.Embed(title="닉네임이 입력되지 않았습니다", description="", color=0x5CD1E5)
                embed.add_field(name="Player nickname not entered",
                                value="To use command !배그솔로 : !배그솔로 (Nickname)", inline=False)
                embed.set_footer(text='Service provided by WH3N_GG#7758.')
                await message.channel.send("Error : Incorrect command usage ", embed=embed)

            else:
                accessors = bs.findAll('a', {'href': re.compile('\/statistics\/[A-Za-z]')})

                # Season Information : ['PUBG',(season info),(Server),'overview']
                seasonInfo = []
                for si in bs.findAll('li', {'class': "active"}):
                    seasonInfo.append(si.text.strip())
                serverAccessorAndStatus = []
                # To prevent : Parsing Server Status, Make a result like Server:\nOnline. So I need to delete '\n'to get good result
                for a in accessors:
                    serverAccessorAndStatus.append(re.sub(pattern='[\n]', repl="", string=a.text.strip()))

                # Varaible serverAccessorAndStatus : [(accessors),(ServerStatus),(Don't needed value)]

                soloQueInfo = bs.find('section', {'class': "solo modeItem"}).find('div', {'class': "mode-section fpp"})
                if soloQueInfo == None:
                    embed = discord.Embed(title="", description="솔로 플레이 내역이 존재하지 않습니다.",
                                          color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    await message.channel.send("PUBG player " + playerNickname + "'s FPP solo que information",
                                               embed=embed)
                else:
                    # print(soloQueInfo)
                    # Get total playtime
                    soloQueTotalPlayTime = soloQueInfo.find('span', {'class': "time_played"}).text.strip()
                    # Get Win/Top10/Lose : [win,top10,lose]
                    soloQueGameWL = soloQueInfo.find('em').text.strip().split(' ')
                    # RankPoint
                    rankPoint = soloQueInfo.find('span', {'class': 'value'}).text
                    # Tier image url, tier
                    tierInfos = soloQueInfo.find('img', {
                        'src': re.compile('\/\/static\.dak\.gg\/images\/icons\/tier\/[A-Za-z0-9_.]')})
                    tierImage = "https:" + tierInfos['src']
                    print(tierImage)
                    tier = tierInfos['alt']

                    # Comprehensive info
                    comInfo = []
                    # [K/D,승률,Top10,평균딜량,게임수, 최다킬수,헤드샷,저격거리,생존,평균순위]
                    for ci in soloQueInfo.findAll('p', {'class': 'value'}):
                        comInfo.append(ci.text.strip())
                    comInfopercentage = []
                    # [전체 상위 %, K/D,승률,Top10,평균딜량,게임수,최다킬수,헤드샷,저격,생존,None]
                    for cif in soloQueInfo.findAll('span', {'class': 'top'}):
                        comInfopercentage.append((cif.text))

                    embed = discord.Embed(title="Player Unkonw Battle Ground player search from dak.gg", description="",
                                          color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    embed.add_field(name="Real Time Accessors and Server Status",
                                    value="Accessors : " + serverAccessorAndStatus[0] + " | " "Server Status : " +
                                          serverAccessorAndStatus[1].split(':')[-1], inline=False)
                    embed.add_field(name="사용자 서버 / 플레이 시간",
                                    value=seasonInfo[2] + " Server / Total playtime : " + soloQueTotalPlayTime,
                                    inline=False)
                    embed.add_field(name="티어 / 최대 티어 / 평균 티어",
                                    value=tier + " (" + rankPoint + "p)" + " / " + comInfopercentage[0] + " / " +
                                          comInfo[-1], inline=False)
                    embed.add_field(name="K/D", value=comInfo[0] + "/" + comInfopercentage[1], inline=True)
                    embed.add_field(name="승률", value=comInfo[1] + "/" + comInfopercentage[2], inline=True)
                    embed.add_field(name="Top 10 비율", value=comInfo[2] + "/" + comInfopercentage[3], inline=True)
                    embed.add_field(name="평균딜량", value=comInfo[3] + "/" + comInfopercentage[4], inline=True)
                    embed.add_field(name="게임수", value=comInfo[4] + "판/" + comInfopercentage[5], inline=True)
                    embed.add_field(name="최다킬수", value=comInfo[5] + "킬/" + comInfopercentage[6], inline=True)
                    embed.add_field(name="헤드샷 비율", value=comInfo[6] + "/" + comInfopercentage[7], inline=True)
                    embed.add_field(name="저격거리", value=comInfo[7] + "/" + comInfopercentage[8], inline=True)
                    embed.add_field(name="평균생존시간", value=comInfo[8] + "/" + comInfopercentage[9], inline=True)
                    embed.set_thumbnail(url=tierImage)
                    embed.set_footer(text='Service provided by WH3N_GG#7758.')
                    await message.channel.send("PUBG player " + playerNickname + "'s FPP solo que information",
                                               embed=embed)
        except HTTPError as e:
            embed = discord.Embed(title="Not existing plyer",
                                  description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",
                                  color=0x5CD1E5)
            await message.channel.send("Error : Not existing player", embed=embed)
        except AttributeError as e:
            embed = discord.Embed(title="Not existing plyer",
                                  description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",
                                  color=0x5CD1E5)
            await message.channel.send("Error : Not existing player", embed=embed)

    if message.content.startswith("!배그듀오2"):
        baseURL = "https://dak.gg/profile/"
        playerNickname = ''.join((message.content).split(' ')[1:])
        URL = baseURL + quote(playerNickname)
        try:
            html = urlopen(URL)
            bs = BeautifulSoup(html, 'html.parser')
            if len(message.content.split(" ")) == 1:
                embed = discord.Embed(title="닉네임이 입력되지 않았습니다", description="", color=0x5CD1E5)
                embed.add_field(name="Player nickname not entered",
                                value="To use command !배그스쿼드 : !배그스쿼드 (Nickname)", inline=False)
                embed.set_footer(text='Service provided by WH3N_GG#7758.')
                await message.channel.send("Error : Incorrect command usage ", embed=embed)

            else:
                accessors = bs.findAll('a', {'href': re.compile('\/statistics\/[A-Za-z]')})

                # Season Information : ['PUBG',(season info),(Server),'overview']
                seasonInfo = []
                for si in bs.findAll('li', {'class': "active"}):
                    seasonInfo.append(si.text.strip())
                serverAccessorAndStatus = []
                # To prevent : Parsing Server Status, Make a result like Server:\nOnline. So I need to delete '\n'to get good result
                for a in accessors:
                    serverAccessorAndStatus.append(re.sub(pattern='[\n]', repl="", string=a.text.strip()))

                # Varaible serverAccessorAndStatus : [(accessors),(ServerStatus),(Don't needed value)]

                duoQueInfo = bs.find('section', {'class': "duo modeItem"}).find('div', {'class': "mode-section fpp"})
                if duoQueInfo == None:
                    embed = discord.Embed(title="플레이 내역이 존재하지 않습니다.", description="듀오 플레이 내역이 존재하지 않습니다.",
                                          color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    await message.channel.send("PUBG player " + playerNickname + "'s FPP duo que information",
                                               embed=embed)
                else:
                    # print(duoQueInfo)
                    # Get total playtime
                    duoQueTotalPlayTime = duoQueInfo.find('span', {'class': "time_played"}).text.strip()
                    # Get Win/Top10/Lose : [win,top10,lose]
                    duoQueGameWL = duoQueInfo.find('em').text.strip().split(' ')
                    # RankPoint
                    rankPoint = duoQueInfo.find('span', {'class': 'value'}).text
                    # Tier image url, tier
                    tierInfos = duoQueInfo.find('img', {
                        'src': re.compile('\/\/static\.dak\.gg\/images\/icons\/tier\/[A-Za-z0-9_.]')})
                    tierImage = "https:" + tierInfos['src']
                    tier = tierInfos['alt']

                    # Comprehensive info
                    comInfo = []
                    # [K/D,승률,Top10,평균딜량,게임수, 최다킬수,헤드샷,저격거리,생존,평균순위]
                    for ci in duoQueInfo.findAll('p', {'class': 'value'}):
                        comInfo.append(ci.text.strip())
                    comInfopercentage = []
                    # [전체 상위 %, K/D,승률,Top10,평균딜량,게임수,최다킬수,헤드샷,저격,생존,None]
                    for cif in duoQueInfo.findAll('span', {'class': 'top'}):
                        comInfopercentage.append((cif.text))

                    embed = discord.Embed(title="Player Unkonw Battle Ground player search from dak.gg", description="",
                                          color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    embed.add_field(name="Real Time Accessors and Server Status",
                                    value="Accessors : " + serverAccessorAndStatus[0] + " | " "Server Status : " +
                                          serverAccessorAndStatus[1].split(':')[-1], inline=False)
                    embed.add_field(name="사용자 서버 / 플레이 시간",
                                    value=seasonInfo[2] + " Server / Total playtime : " + duoQueTotalPlayTime,
                                    inline=False)
                    embed.add_field(name="티어 / 최대 티어 / 평균 티어",
                                    value=tier + " (" + rankPoint + "p)" + " / " + comInfopercentage[0] + " / " +
                                          comInfo[-1], inline=False)
                    embed.add_field(name="K/D", value=comInfo[0] + "/" + comInfopercentage[1], inline=True)
                    embed.add_field(name="승률", value=comInfo[1] + "/" + comInfopercentage[2], inline=True)
                    embed.add_field(name="Top 10 비율", value=comInfo[2] + "/" + comInfopercentage[3], inline=True)
                    embed.add_field(name="평균딜량", value=comInfo[3] + "/" + comInfopercentage[4], inline=True)
                    embed.add_field(name="게임수", value=comInfo[4] + "판/" + comInfopercentage[5], inline=True)
                    embed.add_field(name="최다킬수", value=comInfo[5] + "킬/" + comInfopercentage[6], inline=True)
                    embed.add_field(name="헤드샷 비율", value=comInfo[6] + "/" + comInfopercentage[7], inline=True)
                    embed.add_field(name="저격거리", value=comInfo[7] + "/" + comInfopercentage[8], inline=True)
                    embed.add_field(name="평균생존시간", value=comInfo[8] + "/" + comInfopercentage[9], inline=True)
                    embed.set_thumbnail(url=tierImage)
                    embed.set_footer(text='Service provided by WH3N_GG#7758.')
                    await message.channel.send("PUBG player " + playerNickname + "'s FPP duo que information",
                                               embed=embed)
        except HTTPError as e:
            embed = discord.Embed(title="Not existing plyer",
                                  description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",
                                  color=0x5CD1E5)
            await message.channel.send("Error : Not existing player", embed=embed)
        except AttributeError as e:
            embed = discord.Embed(title="Not existing plyer",
                                  description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",
                                  color=0x5CD1E5)
            await message.channel.send("Error : Not existing player", embed=embed)

    if message.content.startswith("!배그스쿼드2"):
        baseURL = "https://dak.gg/profile/"
        playerNickname = ''.join((message.content).split(' ')[1:])
        URL = baseURL + quote(playerNickname)
        try:
            html = urlopen(URL)
            bs = BeautifulSoup(html, 'html.parser')
            if len(message.content.split(" ")) == 1:
                embed = discord.Embed(title="닉네임이 입력되지 않았습니다", description="", color=0x5CD1E5)
                embed.add_field(name="Player nickname not entered",
                                value="To use command !배그솔로 : !배그솔로 (Nickname)", inline=False)
                embed.set_footer(text='Service provided by WH3N_GG#7758.')
                await message.channel.send("Error : Incorrect command usage ", embed=embed)

            else:
                accessors = bs.findAll('a', {'href': re.compile('\/statistics\/[A-Za-z]')})

                # Season Information : ['PUBG',(season info),(Server),'overview']
                seasonInfo = []
                for si in bs.findAll('li', {'class': "active"}):
                    seasonInfo.append(si.text.strip())
                serverAccessorAndStatus = []
                # To prevent : Parsing Server Status, Make a result like Server:\nOnline. So I need to delete '\n'to get good result
                for a in accessors:
                    serverAccessorAndStatus.append(re.sub(pattern='[\n]', repl="", string=a.text.strip()))

                # Varaible serverAccessorAndStatus : [(accessors),(ServerStatus),(Don't needed value)]

                squadQueInfo = bs.find('section', {'class': "squad modeItem"}).find('div',
                                                                                    {'class': "mode-section fpp"})
                if squadQueInfo == None:
                    embed = discord.Embed(title="기록이 존재하지 않습니다", description="스쿼드 플레이 내역이 존재하지 않습니다.",
                                          color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    await message.channel.send("PUBG player " + playerNickname + "'s FPP squad que information",
                                               embed=embed)
                else:
                    # print(duoQueInfo)
                    # Get total playtime
                    squadQueTotalPlayTime = squadQueInfo.find('span', {'class': "time_played"}).text.strip()
                    # Get Win/Top10/Lose : [win,top10,lose]
                    squadQueGameWL = squadQueInfo.find('em').text.strip().split(' ')
                    # RankPoint
                    rankPoint = squadQueInfo.find('span', {'class': 'value'}).text
                    # Tier image url, tier
                    tierInfos = squadQueInfo.find('img', {
                        'src': re.compile('\/\/static\.dak\.gg\/images\/icons\/tier\/[A-Za-z0-9_.]')})
                    tierImage = "https:" + tierInfos['src']
                    tier = tierInfos['alt']

                    # Comprehensive info
                    comInfo = []
                    # [K/D,승률,Top10,평균딜량,게임수, 최다킬수,헤드샷,저격거리,생존,평균순위]
                    for ci in squadQueInfo.findAll('p', {'class': 'value'}):
                        comInfo.append(ci.text.strip())
                    comInfopercentage = []
                    # [전체 상위 %, K/D,승률,Top10,평균딜량,게임수,최다킬수,헤드샷,저격,생존,None]
                    for cif in squadQueInfo.findAll('span', {'class': 'top'}):
                        comInfopercentage.append((cif.text))

                    embed = discord.Embed(title="Player Unkonw Battle Ground player search from dak.gg", description="",
                                          color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    embed.add_field(name="Real Time Accessors and Server Status",
                                    value="Accessors : " + serverAccessorAndStatus[0] + " | " "Server Status : " +
                                          serverAccessorAndStatus[1].split(':')[-1], inline=False)
                    embed.add_field(name="사용자 서버 / 플레이 시간",
                                    value=seasonInfo[2] + " Server / Total playtime : " + squadQueTotalPlayTime,
                                    inline=False)
                    embed.add_field(name="티어 / 최대 티어 / 평균 티어",
                                    value=tier + " (" + rankPoint + "p)" + " / " + comInfopercentage[0] + " / " +
                                          comInfo[-1], inline=False)
                    embed.add_field(name="K/D", value=comInfo[0] + "/" + comInfopercentage[1], inline=True)
                    embed.add_field(name="승률", value=comInfo[1] + "/" + comInfopercentage[2], inline=True)
                    embed.add_field(name="Top 10 비율", value=comInfo[2] + "/" + comInfopercentage[3], inline=True)
                    embed.add_field(name="평균딜량", value=comInfo[3] + "/" + comInfopercentage[4], inline=True)
                    embed.add_field(name="게임수", value=comInfo[4] + "판/" + comInfopercentage[5], inline=True)
                    embed.add_field(name="최다킬수", value=comInfo[5] + "킬/" + comInfopercentage[6], inline=True)
                    embed.add_field(name="헤드샷 비율", value=comInfo[6] + "/" + comInfopercentage[7], inline=True)
                    embed.add_field(name="저격거리", value=comInfo[7] + "/" + comInfopercentage[8], inline=True)
                    embed.add_field(name="평균생존시간", value=comInfo[8] + "/" + comInfopercentage[9], inline=True)
                    embed.set_thumbnail(url=tierImage)
                    embed.set_footer(text='Service provided by WH3N_GG#7758.')
                    await message.channel.send("PUBG player " + playerNickname + "'s FPP squad que information",
                                               embed=embed)
        except HTTPError as e:
            embed = discord.Embed(title="Not existing plyer",
                                  description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",
                                  color=0x5CD1E5)
            await message.channel.send("Error : Not existing player", embed=embed)
        except AttributeError as e:
            embed = discord.Embed(title="Not existing plyer",
                                  description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",
                                  color=0x5CD1E5)
            await message.channel.send("Error : Not existing player", embed=embed)

    if message.content.startswith("!롤전적"):
        try:
            if len(message.content.split(" ")) == 1:
                embed = discord.Embed(title="소환사 이름이 입력되지 않았습니다!", description="", color=0x5CD1E5)
                embed.add_field(name="Summoner name not entered",
                                value="To use command !롤전적 : !롤전적 (Summoner Nickname)", inline=False)
                embed.set_footer(text='Service provided by WH3N_GG#7758.')
                await message.channel.send("Error : Incorrect command usage ", embed=embed)
            else:
                playerNickname = ''.join((message.content).split(' ')[1:])
                # Open URL
                checkURLBool = urlopen(opggsummonersearch + quote(playerNickname))
                bs = BeautifulSoup(checkURLBool, 'html.parser')

                # 자유랭크 언랭은 뒤에 '?image=q_auto&v=1'표현이없다

                # Patch Note 20200503에서
                # Medal = bs.find('div', {'class': 'ContentWrap tabItems'}) 이렇게 바꾸었었습니다.
                # PC의 설정된 환경 혹은 OS플랫폼에 따라서 ContentWrap tabItems의 띄어쓰기가 인식이

                Medal = bs.find('div', {'class': 'SideContent'})
                RankMedal = Medal.findAll('img', {'src': re.compile('\/\/[a-z]*\-[A-Za-z]*\.[A-Za-z]*\.[A-Za-z]*\/[A-Za-z]*\/[A-Za-z]*\/[a-z0-9_]*\.png')})
                # Variable RankMedal's index 0 : Solo Rank
                # Variable RankMedal's index 1 : Flexible 5v5 rank

                # for mostUsedChampion
                mostUsedChampion = bs.find('div', {'class': 'ChampionName'})
                mostUsedChampionKDA = bs.find('span', {'class': 'KDA'})

                # 솔랭, 자랭 둘다 배치가 안되어있는경우 -> 사용된 챔피언 자체가 없다. 즉 모스트 챔피언 메뉴를 넣을 필요가 없다.

                # Scrape Summoner's Rank information
                # [Solorank,Solorank Tier]
                solorank_Types_and_Tier_Info = deleteTags(bs.findAll('div', {'class': {'RankType', 'TierRank'}}))
                # [Solorank LeaguePoint, Solorank W, Solorank L, Solorank Winratio]
                solorank_Point_and_winratio = deleteTags(
                    bs.findAll('span', {'class': {'LeaguePoints', 'wins', 'losses', 'winratio'}}))
                # [Flex 5:5 Rank,Flexrank Tier,Flextier leaguepoint + W/L,Flextier win ratio]
                flexrank_Types_and_Tier_Info = deleteTags(bs.findAll('div', {
                    'class': {'sub-tier__rank-type', 'sub-tier__rank-tier', 'sub-tier__league-point',
                              'sub-tier__gray-text'}}))
                # ['Flextier W/L]
                flexrank_Point_and_winratio = deleteTags(bs.findAll('span', {'class': {'sub-tier__gray-text'}}))

                # embed.set_imag()는 하나만 들어갈수 있다.

                # 솔랭, 자랭 둘다 배치 안되어있는 경우 -> 모스트 챔피언 출력 X
                if len(solorank_Point_and_winratio) == 0 and len(flexrank_Point_and_winratio) == 0:
                    embed = discord.Embed(title="소환사 전적검색", description="", color=0x5CD1E5)
                    embed.add_field(name="Summoner Search From op.gg", value=opggsummonersearch + playerNickname,
                                    inline=False)
                    embed.add_field(name="Ranked Solo : Unranked", value="Unranked", inline=False)
                    embed.add_field(name="Flex 5:5 Rank : Unranked", value="Unranked", inline=False)
                    embed.set_thumbnail(url='https:' + RankMedal[0]['src'])
                    embed.set_footer(text='Service provided by WH3N_GG#7758.')
                    await message.channel.send("소환사 " + playerNickname + "님의 전적", embed=embed)

                # 솔로랭크 기록이 없는경우
                elif len(solorank_Point_and_winratio) == 0:

                    # most Used Champion Information : Champion Name, KDA, Win Rate
                    mostUsedChampion = bs.find('div', {'class': 'ChampionName'})
                    mostUsedChampion = mostUsedChampion.a.text.strip()
                    mostUsedChampionKDA = bs.find('span', {'class': 'KDA'})
                    mostUsedChampionKDA = mostUsedChampionKDA.text.split(':')[0]
                    mostUsedChampionWinRate = bs.find('div', {'class': "Played"})
                    mostUsedChampionWinRate = mostUsedChampionWinRate.div.text.strip()

                    FlexRankTier = flexrank_Types_and_Tier_Info[0] + ' : ' + flexrank_Types_and_Tier_Info[1]
                    FlexRankPointAndWinRatio = flexrank_Types_and_Tier_Info[2] + " /" + flexrank_Types_and_Tier_Info[-1]
                    embed = discord.Embed(title="소환사 전적검색", description="", color=0x5CD1E5)
                    embed.add_field(name="Summoner Search From op.gg", value=opggsummonersearch + playerNickname,
                                    inline=False)
                    embed.add_field(name="Ranked Solo : Unranked", value="Unranked", inline=False)
                    embed.add_field(name=FlexRankTier, value=FlexRankPointAndWinRatio, inline=False)
                    embed.add_field(name="Most Used Champion : " + mostUsedChampion,
                                    value="KDA : " + mostUsedChampionKDA + " / " + " WinRate : " + mostUsedChampionWinRate,
                                    inline=False)
                    embed.set_thumbnail(url='https:' + RankMedal[1]['src'])
                    embed.set_footer(text='Service provided by WH3N_GG#7758.')
                    await message.channel.send("소환사 " + playerNickname + "님의 전적", embed=embed)

                # 자유랭크 기록이 없는경우
                elif len(flexrank_Point_and_winratio) == 0:

                    # most Used Champion Information : Champion Name, KDA, Win Rate
                    mostUsedChampion = bs.find('div', {'class': 'ChampionName'})
                    mostUsedChampion = mostUsedChampion.a.text.strip()
                    mostUsedChampionKDA = bs.find('span', {'class': 'KDA'})
                    mostUsedChampionKDA = mostUsedChampionKDA.text.split(':')[0]
                    mostUsedChampionWinRate = bs.find('div', {'class': "Played"})
                    mostUsedChampionWinRate = mostUsedChampionWinRate.div.text.strip()

                    SoloRankTier = solorank_Types_and_Tier_Info[0] + ' : ' + solorank_Types_and_Tier_Info[1]
                    SoloRankPointAndWinRatio = solorank_Point_and_winratio[0] + "/ " + solorank_Point_and_winratio[
                        1] + " " + solorank_Point_and_winratio[2] + " /" + solorank_Point_and_winratio[3]
                    embed = discord.Embed(title="소환사 전적검색", description="", color=0x5CD1E5)
                    embed.add_field(name="Summoner Search From op.gg", value=opggsummonersearch + playerNickname,
                                    inline=False)
                    embed.add_field(name=SoloRankTier, value=SoloRankPointAndWinRatio, inline=False)
                    embed.add_field(name="Flex 5:5 Rank : Unranked", value="Unranked", inline=False)
                    embed.add_field(name="Most Used Champion : " + mostUsedChampion,
                                    value="KDA : " + mostUsedChampionKDA + " / " + "WinRate : " + mostUsedChampionWinRate,
                                    inline=False)
                    embed.set_thumbnail(url='https:' + RankMedal[0]['src'])
                    embed.set_footer(text='Service provided by WH3N_GG#7758.')
                    await message.channel.send("소환사 " + playerNickname + "님의 전적", embed=embed)
                # 두가지 유형의 랭크 모두 완료된사람
                else:
                    # 더 높은 티어를 thumbnail에 안착
                    solorankmedal = RankMedal[0]['src'].split('/')[-1].split('?')[0].split('.')[0].split('_')
                    flexrankmedal = RankMedal[1]['src'].split('/')[-1].split('?')[0].split('.')[0].split('_')

                    # Make State
                    SoloRankTier = solorank_Types_and_Tier_Info[0] + ' : ' + solorank_Types_and_Tier_Info[1]
                    SoloRankPointAndWinRatio = solorank_Point_and_winratio[0] + "/ " + solorank_Point_and_winratio[
                        1] + " " + solorank_Point_and_winratio[2] + " /" + solorank_Point_and_winratio[3]
                    FlexRankTier = flexrank_Types_and_Tier_Info[0] + ' : ' + flexrank_Types_and_Tier_Info[1]
                    FlexRankPointAndWinRatio = flexrank_Types_and_Tier_Info[2] + " /" + flexrank_Types_and_Tier_Info[-1]

                    # most Used Champion Information : Champion Name, KDA, Win Rate
                    mostUsedChampion = bs.find('div', {'class': 'ChampionName'})
                    mostUsedChampion = mostUsedChampion.a.text.strip()
                    mostUsedChampionKDA = bs.find('span', {'class': 'KDA'})
                    mostUsedChampionKDA = mostUsedChampionKDA.text.split(':')[0]
                    mostUsedChampionWinRate = bs.find('div', {'class': "Played"})
                    mostUsedChampionWinRate = mostUsedChampionWinRate.div.text.strip()

                    cmpTier = tierCompare(solorankmedal[0], flexrankmedal[0])
                    embed = discord.Embed(title="소환사 전적검색", description="", color=0x5CD1E5)
                    embed.add_field(name="Summoner Search From op.gg", value=opggsummonersearch + playerNickname,
                                    inline=False)
                    embed.add_field(name=SoloRankTier, value=SoloRankPointAndWinRatio, inline=False)
                    embed.add_field(name=FlexRankTier, value=FlexRankPointAndWinRatio, inline=False)
                    embed.add_field(name="Most Used Champion : " + mostUsedChampion,
                                    value="KDA : " + mostUsedChampionKDA + " / " + " WinRate : " + mostUsedChampionWinRate,
                                    inline=False)
                    if cmpTier == 0:
                        embed.set_thumbnail(url='https:' + RankMedal[0]['src'])
                    elif cmpTier == 1:
                        embed.set_thumbnail(url='https:' + RankMedal[1]['src'])
                    else:
                        if solorankmedal[1] > flexrankmedal[1]:
                            embed.set_thumbnail(url='https:' + RankMedal[0]['src'])
                        elif solorankmedal[1] < flexrankmedal[1]:
                            embed.set_thumbnail(url='https:' + RankMedal[0]['src'])
                        else:
                            embed.set_thumbnail(url='https:' + RankMedal[0]['src'])

                    embed.set_footer(text='Service provided by WH3N_GG#7758.')
                    await message.channel.send("소환사 " + playerNickname + "님의 전적", embed=embed)
        except HTTPError as e:
            embed = discord.Embed(title="소환사 전적검색 실패", description="", color=0x5CD1E5)
            embed.add_field(name="", value="올바르지 않은 소환사 이름입니다. 다시 확인해주세요!", inline=False)
            await message.channel.send("Wrong Summoner Nickname")

        except UnicodeEncodeError as e:
            embed = discord.Embed(title="소환사 전적검색 실패", description="", color=0x5CD1E5)
            embed.add_field(name="???", value="올바르지 않은 소환사 이름입니다. 다시 확인해주세요!", inline=False)
            await message.channel.send("Wrong Summoner Nickname", embed=embed)

        except AttributeError as e:
            embed = discord.Embed(title="존재하지 않는 소환사", description="", color=0x5CD1E5)
            embed.add_field(name="해당 닉네임의 소환사가 존재하지 않습니다.", value="소환사 이름을 확인해주세요", inline=False)
            embed.set_footer(text='Service provided by WH3N_GG#7758.')
            await message.channel.send("Error : Non existing Summoner ", embed=embed)
client.run(token)
