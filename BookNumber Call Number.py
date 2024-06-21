import pandas as pd
from jamo import h2j, j2hcj
import re, time, random

ja_list = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
mo_list = "ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ"

def sort_classification(part):
    classification_num, classification  = 0, 0
    
    if not part.isalpha():
        if part[0].isalpha():
            classification = 1
            classification_num = float(part[1:])
        else:
            classification_num = float(part)

    return classification_num, classification   # 분류 기호 알파벳, 븐류 기호 실수


def sort_jamo(first_char):
    first_char_list = [
        [0, 0, 0], [0, 0, 0], [0, 0, 0]
    ]

    for num in range(0, len(first_char)):
        jamo_str = list(j2hcj(h2j(first_char[num])))

        for i in range(0, len(jamo_str)):
            isHangle = False

            if i == 1:
                for mo in mo_list:
                    if jamo_str[i] == mo:
                        first_char_list[num][i] = mo_list.index(mo)
                        isHangle = True
                        break

            if not isHangle:
                for ja in ja_list:
                    if jamo_str[i] == ja:
                        first_char_list[num][i] = ja_list.index(ja)
                        break

    return first_char_list[0], first_char_list[1], first_char_list[2]


def sort_book_codes(book_codes):
    # 초기 변수 설정
    classification_num, classification = 0.0, 0
    first_char_list, first_and_second_char, first_and_third_char = [0, 0, 0], [0, 0, 0], [0, 0, 0]
    second_number = 0.0
    third_char_list, third_and_second_char, third_and_third_char = [0, 0, 0], [0, 0, 0], [0, 0, 0]
    fourth_number = 0.0
    fifth_char_list, fifth_and_second_char, fifth_and_third_char = [0, 0, 0], [0, 0, 0], [0, 0, 0]
    order_copy_char, order_copy_number = 0, 0  # 없으면 0, v = 1, c = 2
    last_copy_char, last_copy_number = 0, 0  # 권차 이후 복본일 경우



    # 분리
    part = book_codes.split()

    # 맨 앞에 "S"로 별치가 붙은 청구기호가 있다. 해당 청구기호를 일반적인 청구기호로 만들어줌
    if part[0] == 'S':
        part.pop(0)
        part.pop(0)

    # *************************************************분류 기호 설정 *************************************************
    # 분류 기호 정렬 기준
    classification_num, classification = sort_classification(part[0])

    # *************************************************저자 기호 설정 *************************************************
    # 저자 기호 저자의 성
    author = part[1]
    author_list = ['', '', '']

    # 저자 기호, 저자의 성, 저자기호 2표, 유휴번호로 3분류
    match = re.findall(r'\d{1,5}', author)
    if match:
        pre_next = author.split(match[0])
        numbers = match[0]
        author_list = [pre_next[0], numbers, pre_next[1]]

    # ㅁ, 미, 민, a, A, Ar 같은 숫자 전 기호 정렬 기준을 설정 ( S - 800 이런 분류 기호인 경우는 제외 )
    if author_list[0] != '':
        first_char_list, first_and_second_char, first_and_third_char = sort_jamo(author_list[0])

    # 저자 기호 두번째 17, 265, 2315, 69125 와 같은 숫자를 분류 (저자의 두번째 글자를 숫자로 치환한 것 : 리재필 저자 기호 제 2표)
    second_number = '0.' + author_list[1]
    second_number = float(second_number)

    # 저자 기호 세번째 숫자 뒤 ㅈ, 장, a, al, al7 등을 분류
    third = author_list[2]

    if third != '':
        third_list = ['', '', '']

        match = re.findall(r'\d{1,5}', third)
        if match:
            pre_next = third.split(match[0])
            numbers = match[0]
            third_list = [pre_next[0], numbers, pre_next[1]]
        else:
            third_list = [third, '', '']

        # ㅁ, 미, 민, a, A, Ar 같은 숫자 전 기호 정렬 기준을 설정 ( S - 800 이런 분류 기호인 경우는 제외 )
        if third_list[0] != '':
            third_char_list, third_and_second_char, third_and_third_char = sort_jamo(third_list[0])

        if third_list[1] != '':
            fourth_number = '0.' + third_list[1]
            fourth_number = float(fourth_number)

        # 마지막 저자 기호 분류
        fifth = third_list[2]
        if fifth != '':
            fifth_char_list, fifth_and_second_char, fifth_and_third_char = sort_jamo(fifth)

    # *************************************************권차 및 복본 설정 *************************************************

    # 권차 및 복본 기호가 있다면
    if len(part) > 2:
        order = part[2].split('.')
        if order[1] == '' and len(part) > 3:
            order[1] = part[3]
            part.pop(3)

        if order[0] == 'v':
            order_copy_char = 1
        elif order[0] == 'c':
            order_copy_char = 2

        if order[1] == '':
            order_copy_number = int(part[3])
        else:
            order_copy_number = int(order[1])


        if len(part) >= 4 and '.' in part[3]:
            print("parpartpartpartt  ", part)

            copy = part[3].split('.')
            if copy[1] == '' and len(part) > 4:
                copy[1] = part[4]
                part.pop(4)

            if copy[0] == 'v':
                last_copy_char = 1
            elif copy[0] == 'c':
                last_copy_char = 2

            if copy[1] == '':
                last_copy_number = int(part[3])
            else:
                last_copy_number = int(copy[1])

    # 정렬 기준
    # 분류기호 숫자 -> 분류 별치 기호
    # ->저자기호 저자의 성(한글[자음 -> 모음 -> 자음+모음] -> 영문)
    #   -> 저자기호 저자 이름 두번째 글자 (이재필 저자기호 제 2표)
    #       -> 저자기호 책 제목의 첫글자 (한글[자음 -> 모음 -> 자음+모음] -> 영문)
    #           -> 유휴기호 (숫자 -> 한글[자음 -> 모음 -> 자음+모음] -> 영문)
    #               -> 권차 및 복본 기호 (v.1 - c.1이면 v가 먼저, 이후 숫자 )
    return (
        classification_num, classification,

        first_char_list, first_and_second_char, first_and_third_char,
        second_number,
        third_char_list, third_and_second_char, third_and_third_char,
        fourth_number,
        fifth_char_list, fifth_and_second_char, fifth_and_third_char,

        order_copy_char, order_copy_number,
        last_copy_char, last_copy_number
    )


if __name__ == "__main__":

    start_time = time.time()

    # 엑셀 파일 열기
    print("\n엑셀 파일 불러오는 중...")
    data = pd.read_excel("20240621-00-11-37.xlsx")
    call_numbers = list(data.iloc[:, 2])

    # 전, 현재, 후를 기준으로 정배열 오류를 찾기
    correct_order = []
    for i in range(len(call_numbers)):
        if i == 0 or i == len(call_numbers) - 1:
            # 첫 번째와 마지막 행은 True로 설정
            correct_order.append(True)
        else:
            prev_code = call_numbers[i - 1]
            curr_code = call_numbers[i]
            next_code = call_numbers[i + 1]
            if (sort_book_codes(prev_code) <= sort_book_codes(curr_code) <= sort_book_codes(next_code)):
                correct_order.append(True)
            else:
                correct_order.append(False)

    # 결과 출력 및 엑셀 저장
    formatted_date = "청구기호_정배열_작업_완료.xlsx"
    df = pd.DataFrame({
        '청구기호 작업 전': call_numbers,
        '올바른 순서 여부': correct_order
    })
    df.to_excel(formatted_date, index=False)

    exit(0)

    # 청구기호 정배열하기
    sorted_codes = sorted(call_numbers[:], key=sort_book_codes)

    # 정렬된 결과 출력
    index = 1
    for code in sorted_codes:
        print(index, " : ", code)
        index += 1

    formatted_date = "청구기호 정배열 작업 완료.xlsx"
    df = pd.DataFrame({
        '청구기호 작업 전': call_numbers,
        '청구기호 정배열': sorted_codes
    })
    df.to_excel(formatted_date, index=False)

    print("경과 시간 : %.3f초"%(time.time() - start_time))
