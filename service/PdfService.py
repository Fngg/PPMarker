from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate,LongTable, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY


# 基本设置
# 默认不支持中文，需要注册字体
stylesheet = getSampleStyleSheet()  # 获取样式集
# 获取reportlab自带样式
Normal = stylesheet['Normal']
BodyText = stylesheet['BodyText']
Italic = stylesheet['Italic']
Title = stylesheet['Title']
Heading1 = stylesheet['Heading1']
Heading2 = stylesheet['Heading2']
Heading3 = stylesheet['Heading3']
Heading4 = stylesheet['Heading4']
Heading5 = stylesheet['Heading5']
Heading6 = stylesheet['Heading6']
Bullet = stylesheet['Bullet']
Definition = stylesheet['Definition']
Code = stylesheet['Code']

# 自带样式不支持中文，需要设置中文字体，但有些样式会丢失，如斜体Italic。有待后续发现完全兼容的中文字体
Normal.fontName = 'SimSun'
Italic.fontName = 'SimSun'
BodyText.fontName = 'SimSun'
Title.fontName = 'SimSun'
Heading1.fontName = 'SimSun'
Heading2.fontName = 'SimSun'
Heading3.fontName = 'SimSun'
Heading4.fontName = 'SimSun'
Heading5.fontName = 'SimSun'
Heading6.fontName = 'SimSun'
Bullet.fontName = 'SimSun'
Definition.fontName = 'SimSun'
Code.fontName = 'SimSun'


# 添加自定义样式
stylesheet.add(
    ParagraphStyle(name='body',
                   fontName="SimSun",
                   fontSize=10,
                   textColor='black',
                   leading=20,  # 行间距
                   spaceBefore=0,  # 段前间距
                   spaceAfter=10,  # 段后间距
                   leftIndent=0,  # 左缩进
                   rightIndent=0,  # 右缩进
                   firstLineIndent=20,  # 首行缩进，每个汉字为10
                   alignment=TA_JUSTIFY,  # 对齐方式

                   # bulletFontSize=15,       #bullet为项目符号相关的设置
                   # bulletIndent=-50,
                   # bulletAnchor='start',
                   # bulletFontName='Symbol'
                   )
)
body = stylesheet['body']


class ResultPdf(object):
    def __init__(self,file_path,title):
        self.file_path = file_path
        self.story = []
        self.story.append(Paragraph(title, Title))
        self.index = 1
        self.doc = SimpleDocTemplate(self.file_path)

    def add_graph(self,step,graph_path):
        self.story.append(Paragraph( step, Heading2))
        self.story.append(Paragraph(f"<img src='{graph_path}' valign='top'/><br/><br/><br/><br/><br/>", body))

    def add_content(self,step,text):
        self.story.append(Paragraph(str(self.index)+"."+step, Heading2))
        self.index += 1
        self.story.append(Paragraph(text, body))

    def add_simple_content(self,text):
        self.story.append(Paragraph(text, body))

    def add_simple_title(self,step):
        self.story.append(Paragraph(step, Heading3))

    # 绘制表格
    def add_table(self,data):
        if data and len(data)>=1:
            cols = len(data[0])
            tableStyle = [
                ('FONTNAME', (0, 0), (-1, -1), 'SimSun'),  # 字体
                ('BACKGROUND', (0, 0), (-1, 0), '#d5dae6'),  # 设置第一行背景颜色
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # 对齐
                ('VALIGN', (-1, 0), (-2, 0), 'MIDDLE'),  # 对齐
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),  # 设置表格框线为grey色，线宽为0.5
            ]
            # 设置表格的自动换行
            data2 = []
            for row in data:
                tmp = []
                for cell in row:
                    if cell:
                        tmp.append(Paragraph(str(cell),Normal))
                    else:
                        tmp.append(Paragraph("",Normal))
                data2.append(tmp)
            colwidths = [self.doc.width / cols for i in range(cols)]
            t = LongTable(data2, colWidths=colwidths)
            t.setStyle(TableStyle(tableStyle))
            self.story.append(t)

    def create(self):
        self.doc.build(self.story)

