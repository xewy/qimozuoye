import jieba
import requests
import stopwords
import streamlit as st
from streamlit_echarts import st_echarts
from collections import Counter
import re
import string
from bs4 import BeautifulSoup
from langdetect import detect
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# 定义数据清洗函数
def clean_text(text):
    text = text.replace('\n', '')
    text = text.replace(' ', '')
    text = text.strip()
    return text


# 定义分词函数
def segment_chinese(text):
    stopwords = ['的', '了', '在', '是', '我', '你', '他', '她', '它', '们', '这', '那', '之', '与', '和', '或', '虽然',
                 '但是', '然而', '因此']
    punctuation = "、，。！？；：“”‘’~@#￥%……&*（）【】｛｝+-*/=《》<>「」『』【】〔〕｟｠«»“”‘’'':;,/\\|[]{}()$^"
    text = text.translate(str.maketrans("", "", punctuation)).replace('\n', '')
    words = jieba.lcut(text)
    words = [word for word in words if word not in stopwords]
    return words


def segment_english(text):
    stopwords = set(stopwords.words('english'))
    words = re.findall(r'\b\w+\b', text.lower())
    words = [word for word in words if word not in stopwords and word not in string.punctuation]
    return words


# 移除标点符号和数字
def remove_punctuation(text):
    punctuation = string.punctuation
    text = text.translate(str.maketrans('', '', punctuation))
    return re.sub('\d+', '', text)


# 移除HTML标签
def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


# 从HTML中提取正文文本
def extract_body_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.find('body').get_text()
    return text


# 生成词云图
def generate_wordcloud(words):
    wordcloud = WordCloud(font_path ="C:/Windows/Fonts/msyh.ttc",width=800, height=400, background_color='white').generate(' '.join(words))
    return wordcloud


def main():
    st.set_page_config(page_title="网页文本分析工具", page_icon="📊", layout="wide")

    st.title("📊 网页文本分析工具")
    st.write("请输入一个网页链接，我们将为您提取其中的文本，并展示词频统计图。")

    url = st.text_input('输入网页链接:', '')

    if st.button('开始分析'):
        if url:
            st.write("正在分析，请稍候...")
            try:
                r = requests.get(url)
                r.encoding = 'utf-8'
                text = r.text
                text = extract_body_text(text)
                text = remove_html_tags(text)
                text = remove_punctuation(text)
                text = clean_text(text)

                # 自动检测语言
                language = detect(text)
                if language == 'zh-cn':
                    words = segment_chinese(text)
                else:
                    words = segment_english(text)

                word_counts = Counter(words)
                top_words = word_counts.most_common(20)

                # 生成柱状图
                bar_options = {
                    "tooltip": {
                        "trigger": 'item',
                        "formatter": '{b} : {c}'
                    },
                    "xAxis": [{
                        "type": "category",
                        "data": [word for word, count in top_words],
                        "axisLabel": {
                            "interval": 0,
                            "rotate": 30
                        }
                    }],
                    "yAxis": [{"type": "value"}],
                    "series": [{
                        "type": "bar",
                        "data": [count for word, count in top_words]
                    }]
                }

                st.subheader("词频柱状图")
                st_echarts(bar_options, height='500px')

                # 生成词云图
                st.subheader("词云图")
                wordcloud = generate_wordcloud(words)
                fig, ax = plt.subplots()
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)

                st.success("分析完成！")
            except Exception as e:
                st.error(f"分析失败: {e}")
        else:
            st.warning("请输入有效的网页链接")


if __name__ == "__main__":
    main()
