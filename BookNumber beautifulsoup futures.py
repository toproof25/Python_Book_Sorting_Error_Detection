import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import datetime

import concurrent.futures


from collections import OrderedDict

# 전역 변수 초기화
Book_Title = OrderedDict()  # 책 제목
Book_Number = OrderedDict()  # 등록번호
Call_Number = OrderedDict()  # 청구기호
Holding_Institution = OrderedDict()  # 소장처
Loan_Status = OrderedDict()  # 대출정보
Loan_Information = OrderedDict()  # 반납예정일
urls = OrderedDict()  # 책 URL 주소


delay_seconds = 2  # 0.5초 지연
def process_data(BookNumber):

    time.sleep(delay_seconds)

    response = requests.get("https://lib.kangnam.ac.kr/Search/?q="+BookNumber)

    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
    else:
        print("웹에 접근할 수 없습니다.")
        return

    #print("\n[등록번호] 검색 : %s" % (BookNumber))

    book_title_text = soup.select_one(
        '#searchq01 > div.search-list-result > div.sponge-list-content > div.sponge-list-title > a').get_text().strip()

    tr_elements = soup.select(
        '#searchq01 > div.search-list-result > div.search-list-command > div > div > table > tbody > tr')

    for tr in tr_elements:
        td_elements = tr.find_all('td')

        book_number_text = td_elements[0].get_text().strip()
        call_number_text = td_elements[1].get_text().strip()
        holding_institution_text = td_elements[2].get_text().strip()
        loan_status_text = td_elements[3].get_text().strip()
        loan_information_text = td_elements[4].get_text().strip()

        if BookNumber == book_number_text:
            #print("****%s 등록번호 찾기 완료****" % book_number_text)
            #print("책 제목 : ", book_title_text)
            #print("등록번호 : ", book_number_text)
            #print("청구기호 : ", call_number_text)
            #print("소장정보 : ", holding_institution_text)
            #print("대출여부 : ", loan_status_text)
            #print("반납예정 : ", loan_information_text)
            #print("******************************************\n")

            Book_Title[BookNumber] = book_title_text
            Book_Number[BookNumber] = book_number_text
            Call_Number[BookNumber] = call_number_text
            Holding_Institution[BookNumber] = holding_institution_text
            Loan_Status[BookNumber] = loan_status_text
            Loan_Information[BookNumber] = loan_information_text


if __name__ == "__main__":
    # 현재 시간 설정
    now = datetime.datetime.now()
    formatted_date = now.strftime("%Y%m%d-%H-%M-%S") + ".xlsx"

    # 엑셀 파일 열기
    print("엑셀 파일 불러오는 중...")
    data = pd.read_excel("BookNumber.xlsx", sheet_name="800번대")
    book_number_list = list(data.iloc[:, 0])

    # 스크래핑 개수
    limit = 100

    # 각 요소에 대한 설정 (최대 100개)
    print("스크래핑을 위한 설정중입니다...")
    for BookNumber in book_number_list[:limit]:
        Book_Title[BookNumber] = ''
        Book_Number[BookNumber] = ''
        Call_Number[BookNumber] = ''
        Holding_Institution[BookNumber] = ''
        Loan_Status[BookNumber] = ''
        Loan_Information[BookNumber] = ''
        #urls[BookNumber] = ("https://lib.kangnam.ac.kr/Search/?q=" + BookNumber)

    print("총 %d개의 등록번호 중 %d개를 스크래핑합니다." % (len(book_number_list), limit))

    # 시작 시간
    start_time = time.time()

    # 멀티스레드로 스크래핑 작업 실행
    print("..스크랩 시작..\n\n")
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(process_data, book_number_list[:limit])

    # 경과 시간
    end_time = time.time()
    elapsed_time = end_time - start_time
    print("스크래핑 종료 | 경과 시간 : %f" % elapsed_time)

    # 결과를 엑셀 파일로 저장
    print("엑셀 파일로 저장합니다.\n")
    print("책 제목 행 개수 : ", len(Book_Title))
    print("등록번호 행 개수 : ", len(Book_Number))
    print("청구기호 행 개수 : ", len(Call_Number))
    print("소장처 행 개수 : ", len(Holding_Institution))
    print("대출여부 행 개수 : ", len(Loan_Status))
    print("반납예정일 행 개수 : ", len(Loan_Information))

    df = pd.DataFrame({
        '책 제목': Book_Title.values(),
        '등록번호': Book_Number.values(),
        '청구기호': Call_Number.values(),
        '소장처': Holding_Institution.values(),
        '대출정보': Loan_Status.values(),
        '반납예정일': Loan_Information.values()
    })

    df.to_excel(formatted_date, index=False)
    print("엑셀파일 저장 완료... 프로그램 종료")
