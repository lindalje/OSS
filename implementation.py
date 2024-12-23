# OSS project by 이재은
# 웹 크롤링을 이용한 간편 네이버 뉴스 검색창
# 오픈소스 : naver news crawling

from naver_news_crawling_02 import crawler
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon

# 클래스 정의 - 캘린더
# 검색날짜 입력칸, 날짜 변경, 날짜 범위 설정
class Calendar():
    def __init__(self,month):
        self.qdateedit=QDateEdit(calendarPopup=True)
        self.qdateedit.setDateTime(QDateTime.currentDateTime().addMonths(month))
        self.date=self.qdateedit.date()
        # 날짜 변경 감지
        self.qdateedit.dateChanged.connect(self.date_changed)
    # 날짜 변경 이벤트 - 창에 날짜가 변경될때 날짜를 저장한다
    def date_changed(self):
        self.date=self.qdateedit.date()
    # 인스턴스에 저장된 날짜를 반환한다
    def export_date(self):
        return str(self.date.year()) , str(self.date.month()).zfill(2), str(self.date.day()).zfill(2)

# 클래스 정의 - 뉴스 창 (1줄)
# 뉴스 검색 결과 표시 
class ArticleRow():
    def __init__(self,i):
        self.qls_article=[QLabel() for _ in range(6)]
        self.qls_article[0]=QLabel(f"뉴스{i+1}")
        for label in self.qls_article:
            label.setFixedHeight(80)
            label.setFixedWidth(140)
            label.setWordWrap(True)
            label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.qls_article[2].setFixedWidth(200)
        self.qls_article[4].setFixedWidth(600)
        self.qls_article[5].setFixedWidth(200)
    # 뉴스 정보를 창에 업데이트
    # dict : 뉴스 정보를 포함한 딕셔너리, col : 몇번째 뉴스인지
    def settext(self,dict,col):
        label=['date','title','source','contents','link']
        for i in range(5):
            self.qls_article[i+1].setText("") # 창 초기화
            if len(dict[label[i]])>col:
                self.qls_article[i+1].setText(dict[label[i]][col])
    

# 메인 화면 설정
class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        self.adjust_var()
        self.initUI()

    # 뉴스 수집 관련 변수
    def adjust_var(self):
        self.maxpage=1 # 화면 크기 제한으로 1페이지만 수집!
        self.query="속보"
        self.sort="0" #관련도순
        self.result={"date" : [ "" for i in range(10)] , "title":[ "" for i in range(10)]  ,  "source" :[ "" for i in range(10)]   ,"contents":[ "" for i in range(10)]   ,"link":[ "" for i in range(10)]   }

    #UI 설정
    def initUI(self):
        self.setWindowTitle('News search window')
        # 메인 블록
        self.move(100, 100)
        self.resize(800, 800)
        self.setWindowIcon(QIcon('front_image.png'))

        # vbox에 아이템을 추가하는 형식
        vbox=QVBoxLayout()
        self.setLayout(vbox)

# Line 1 (제목)
        title_box=QHBoxLayout()
        title_box.addStretch(1)
        title=QLabel("네이버 뉴스 검색기")
        title.setStyleSheet("background-color:green;"
                      "font:17pt Trebuchet MS;"
                      "border-style: solid;"
                      "border-width: 2px;"
                      "border-color: #000000;"
                      "border-radius: 2px")
        title_box.addWidget(title)
        title_box.addStretch(1)

        vbox.addLayout(title_box)

# Line 2 (검색어)
        query= QHBoxLayout()
        query.addStretch(1)
        query.addWidget(QLabel('검색어:'))
        ql_query= QLineEdit(self)
        ql_query.setText(self.query)
        ql_query.textChanged[str].connect(self.query_change)
        query.addWidget(ql_query)
        query.addStretch(1)

        vbox.addLayout(query)

# Line 3 (검색 기간) 
        hbox_date=QHBoxLayout()
        self.sCal=Calendar(-1)
        self.eCal=Calendar(0)

        hbox_date.addStretch(1)
        hbox_date.addWidget(QLabel("기간"))
        hbox_date.addWidget(self.sCal.qdateedit)
        hbox_date.addWidget(QLabel("~"))
        hbox_date.addWidget(self.eCal.qdateedit)
        hbox_date.addStretch(1)

        vbox.addLayout(hbox_date)

# Line 4 연관도/최신순/오래순
        hbox_radio=QHBoxLayout()
        self.radio_related=QRadioButton("관련도순")
        self.radio_related.setChecked(True)
        self.radio_new=QRadioButton("최신순")
        self.radio_old=QRadioButton("오래된순")
        self.radio_related.clicked.connect(self.radio_clicked)
        self.radio_new.clicked.connect(self.radio_clicked)
        self.radio_old.clicked.connect(self.radio_clicked)
        hbox_radio.addStretch(1)
        hbox_radio.addWidget(self.radio_related)
        hbox_radio.addWidget(self.radio_new)
        hbox_radio.addWidget(self.radio_old)
        hbox_radio.addStretch(1)

        vbox.addLayout(hbox_radio)

#Line 5 (시작버튼)
        hbox_start=QHBoxLayout()
        hbox_start.addStretch(1)
        start_btn=QPushButton('검색',self)
        start_btn.clicked.connect(self.run)
        hbox_start.addWidget(start_btn)
        hbox_start.addStretch(1)

        vbox.addLayout(hbox_start)

# 뉴스 출력
        article_grid=QGridLayout()
        header_label=['뉴스','날짜','제목','출처','요약','링크']
        for j in range(6):
            label=QLabel(header_label[j])
            label.setFixedHeight(80)
            label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            label.setStyleSheet(""
                      "border-style: solid;"
                      "border-width: 2px;"
                      "border-color: #000000;"
                      "border-radius: 3px")

            article_grid.addWidget(label,0,j)

        self.article=[ArticleRow(i) for i in range(5)]
        for i in range(5):
            for j in range(6):
                article_grid.addWidget(self.article[i].qls_article[j],i+1,j)

        vbox.addLayout(article_grid)

        self.show()

    # input 수정 이벤트 -Line 2가 호출
    # 검색어를 입력/수정할때마다 갱신한다
    def query_change(self, text):
        self.query=text
    # 관련순/최신순/오래된순 수정 이벤트 - Line 4가 호출
    def radio_clicked(self):
        if self.radio_related.isChecked():
            self.sort="0"
        elif self.radio_new.isChecked():
            self.sort="1"
        elif self.radio_old.isChecked():
            self.sort="2"
        else:
            print("error!")
    # 검색 이벤트 - Line 5가 호출
    def run(self):
        syear, smonth, sday = self.sCal.export_date()
        eyear, emonth, eday= self.eCal.export_date()
        s_date=syear+"."+smonth+"."+sday
        e_date=eyear+"."+emonth+"."+eday
        # 웹 크롤러 오픈소스를 통해 뉴스 정보를 가져온다
        self.result=crawler(self.maxpage,self.query,self.sort,s_date,e_date)
        # 창에 정보를 갱신한다
        for i in range(5):
            self.article[i].settext(self.result,i)

# 메인함수
# pyqt5 창을 실행한다
if __name__ == '__main__':

   app = QApplication(sys.argv)
   ex = MyApp()
   sys.exit(app.exec_())