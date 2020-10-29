import re
from bs4 import BeautifulSoup
import string
import MeCab
from gensim.summarization.summarizer import summarize as textrank_summarizer
from gensim.summarization.textcleaner import clean_text_by_sentences


# tags = ['NNG','NNP','NNBC', 'NR', # 일반 명사, 고유 명사, 단위를 나타내는 명사, 수사, 
#             'VV','VA','VCP','VCN',   # 동사, 긍정 지정사, 부정 지정사
#             'XR',   # 어근, 붙임표(물결,숨김,빠짐)/기타기호 (논리수학기호,화폐기호) 'SY',
#             'SL', 'SH', ]  # 외국어, 한자, 숫자'SN'
def korean_tokenizer(text, use_tags=None, print_tag=False): 
    tokenizer = MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ko-dic")
    parsed = tokenizer.parse(text)
    word_tag = [w for w in parsed.split("\n")]
    result = []
    
    if use_tags:
        for word_ in word_tag[:-2]:
            word = word_.split("\t")
            tag = word[1].split(",")[0]

            if(tag in use_tags):     
                if print_tag:
                    result.append((word[0], tag))
                else:
                    result.append(word[0]) 
    else:
        for word_ in word_tag[:-2]:
            word = word_.split("\t")
            result.append(word[0]) 

    return result


def preprocessing(text, tokenizer=korean_tokenizer):
    text_p = noise_remover(text)
    if tokenizer is not None:
        text_p = tokenizer(text_p)
        text_p = ' '.join(text_p)
    
    # print("-------------------------text_p---------------------------------")
    # print(text_p)
    text_ps = summarizer(text_p)
    # print("-------------------------text_ps---------------------------------")
    # print(text_ps)
    # print()
    return text_ps



def noise_remover(text):
    text = text.lower()
    
    # url 대체
    url_pattern = re.compile(r'https?://\S*|www\.\S*')
    text = url_pattern.sub(r'URL', text)

    # html 삭제
    soup = BeautifulSoup(text, "html.parser")
    text = soup.get_text(separator=" ")

    # 숫자 중간에 공백 삽입하기
    text = number_splitter(text)
    #number_pattern = re.compile('\w*\d\w*') 
#     number_pattern = re.compile('\d+') 
#     text = number_pattern.sub(r'[[NUMBER]]', text)
    

    # PUCTUACTION_TO_REMOVED = string.punctuation.translate(str.maketrans('', '', '\"\'#$%&\\@'))  # !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ 중 적은것을 제외한 나머지를 삭제
    # text = text.translate(str.maketrans(PUCTUACTION_TO_REMOVED, ' '*len(PUCTUACTION_TO_REMOVED))) 

    # remove_redundant_white_spaces
    text = re.sub(' +', ' ', text)
    
    return text


def number_splitter(sentence):
    # 1. 공백 이후 숫자로 시작하는 경우만(문자+숫자+문자, 문자+숫자 케이스는 제외), 해당 숫자와 그 뒤 문자를 분리
    num_str_pattern = re.compile(r'(\s\d+)([^\d\s])')
    sentence = re.sub(num_str_pattern, r'\1 \2', sentence)

    # 2. 공백으로 sentence를 분리 후 숫자인경우만 공백 넣어주기
    #numbers_reg = re.compile("\s\d{2,}\s")
    sentence_fixed = ''
    for token in sentence.split():
        if token.isnumeric():
            token = ' '.join(token)
        sentence_fixed+=' '+token
    return sentence_fixed


def summarizer(text, word_count=256):
    # Check if the text is too short.
    INPUT_MIN_LENGTH = 10
    sentences = clean_text_by_sentences(text)
    if len(sentences) < INPUT_MIN_LENGTH:
        return text

    text_summarized = textrank_summarizer(text, word_count=word_count)
    text_summarized = re.sub('\n', ' ',text_summarized)
    if len(text_summarized) == 0:
        return text
    
    return text_summarized
