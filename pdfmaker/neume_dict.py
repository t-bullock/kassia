#!/usr/bin/python
# -*- coding: utf-8 -*-

def translate(text):
    splitText = text.split(" ")
    tmpText = [t for t in splitText]
    # might need to add in a str replace for two vareia in a row
    return u''.join(tmpText)

def takesLyric(neume):
    return neume in neumesWithLyrics

def standAlone(neume):
    return neume in standAloneNeumes

def chunkNeumes(neumeText):
    """Breaks neumeArray into logical chunks based on whether a linebreak
    can occur between them"""
    neumeArray = neumeText.split(' ')
    chunkArray = []   
    i = 0
    while(i < len(neumeArray)):
        # Grab next neume
        chunk = neumeArray[i]
        # Add more neumes to chunk like fthora, ison, etc
        j = 1
        if (i+1) < len(neumeArray):
            while((not standAlone(neumeArray[i+j])) and (neumeArray[i+j] != "\\")):
                chunk += " " + neumeArray[i+j]
                j += 1
                if (i+j >= len(neumeArray)):
                    print "At the end!"
                    break
        i += j
        chunkArray.append(chunk)
        # Check if we're at the end of the array
        if i >= len(neumeArray):
            break
        
        
    return chunkArray


neumesWithLyrics = ['a','A',u'å',u'Å','e','E','h','H',u'˙',
                u'Ó','i','I',u'ˆ','j','J',u'∆',u'Ô','k','K',u'˚',u'','l','m',
                'M',u'µ',u'Â','n','o','O',u'ø','p','P',u'π',u'∏','q','Q',u'œ',
                u'Œ','s','S',u'ß',u'Í','U',u'¨','v','V',u'√',u'◊','w','W',
                u'∑',u'„',u'˛','y','Y',u'Á','(','_',u'±',u'”',u'«',
                u'≤',u'Æ','>',u'è',u'é',u'á',u'ü',u'¨',u'ê',u'û',
                u'ã',u'À',u'Õ',u'Ã',u'Ö',u'Ü',u'Ô',u'Â']

standAloneNeumes = ['a','A',u'å',u'Å','b','B',u'∫',u'ı','e','E','h','H',u'˙',
                u'Ó','i','I',u'ˆ','j','J',u'∆',u'Ô','k','K',u'˚',u'','l','m',
                'M',u'µ',u'Â','n','o','O',u'ø','p','P',u'π',u'∏','q','Q',u'œ',
                u'Œ','s','S',u'ß',u'Í',u'†','U',u'¨','v','V',u'√',u'◊','w','W',
                u'∑',u'„',u'˛','y','Y',u'Á',u'Ω','(','_',u'±',u'”','\\','|',u'«',
                u'≤',u'Æ','.','>','?',u'÷',u'è',u'é'u'á',u'ü',u'¨',u'ê',u'û',
                u'ã',u'À',u'Õ',u'Ã',u'Ö',u'Ü',u'Ô',u'Â']
