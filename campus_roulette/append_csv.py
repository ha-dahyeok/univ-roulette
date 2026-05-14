import csv

append_text = """고려대학교 서울캠퍼스,대성집,"육류,고기",정문,2,https://place.map.kakao.com/15291402
고려대학교 서울캠퍼스,일미통닭,치킨,정문,2,https://place.map.kakao.com/10901511
고려대학교 서울캠퍼스,마늘과올리브,이탈리안,"정문,법학관 입구",2,https://place.map.kakao.com/17154569
고려대학교 서울캠퍼스,끄티식당,일식,정문,1,https://place.map.kakao.com/621115858
고려대학교 서울캠퍼스,우정초밥,초밥,정문,3,https://place.map.kakao.com/1445761358
고려대학교 서울캠퍼스,황적,"육류,고기",정문,2,https://place.map.kakao.com/1407632617
고려대학교 서울캠퍼스,공주칼국수,칼국수,법학관 입구,1,https://place.map.kakao.com/11629851
고려대학교 서울캠퍼스,호만두,분식,법학관 입구,1,https://place.map.kakao.com/16147294
고려대학교 서울캠퍼스,전주식당,백반,법학관 입구,1,https://place.map.kakao.com/14605927
고려대학교 서울캠퍼스,칠백집,"육류,고기",법학관 입구,2,https://place.map.kakao.com/26425330
고려대학교 서울캠퍼스,모심,백반,법학관 입구,1,https://place.map.kakao.com/10986754
고려대학교 서울캠퍼스,영철버거,햄버거,정경대학 입구,1,https://place.map.kakao.com/10531557
고려대학교 서울캠퍼스,무르무르 드 구스토,양식,정경대학 입구,3,https://place.map.kakao.com/26500779
고려대학교 서울캠퍼스,비야,부대찌개,정경대학 입구,1,https://place.map.kakao.com/11186716
고려대학교 서울캠퍼스,이세돈까스,돈까스,정경대학 입구,1,https://place.map.kakao.com/15296839
고려대학교 서울캠퍼스,어흥식당,스테이크,정경대학 입구,1,https://place.map.kakao.com/476906560
고려대학교 서울캠퍼스,쿠이도라쿠,일식,"정경대학 입구,자연계캠퍼스 입구",1,https://place.map.kakao.com/10901518
고려대학교 서울캠퍼스,철판남,일식,정경대학 입구,2,https://place.map.kakao.com/26456093
고려대학교 서울캠퍼스,한잔의추억,술집,정경대학 입구,2,https://place.map.kakao.com/10531558
고려대학교 서울캠퍼스,발리다포차,술집,정경대학 입구,2,https://place.map.kakao.com/1647895240
고려대학교 서울캠퍼스,미각,중식,정경대학 입구,2,https://place.map.kakao.com/23758362
고려대학교 서울캠퍼스,애기능식당,한식,자연계캠퍼스 입구,1,https://place.map.kakao.com/16499318
고려대학교 서울캠퍼스,서병장대김일병,한식,자연계캠퍼스 입구,1,https://place.map.kakao.com/11186715
고려대학교 서울캠퍼스,탄,일식,자연계캠퍼스 입구,1,https://place.map.kakao.com/11186717
고려대학교 서울캠퍼스,가야가야,일식,자연계캠퍼스 입구,1,https://place.map.kakao.com/11186719
고려대학교 서울캠퍼스,은화수식당,경양식,자연계캠퍼스 입구,1,https://place.map.kakao.com/11186720
고려대학교 서울캠퍼스,춘자,술집,자연계캠퍼스 입구,1,https://place.map.kakao.com/11186721
고려대학교 서울캠퍼스,뽀뽀분식,분식,"정운오IT교양관 후문,자연계캠퍼스 후문",1,https://place.map.kakao.com/11186723
고려대학교 서울캠퍼스,형제집,"육류,고기","정운오IT교양관 후문,자연계캠퍼스 후문",1,https://place.map.kakao.com/11186725
고려대학교 서울캠퍼스,언니네반점,중식,"정운오IT교양관 후문,자연계캠퍼스 후문",1,https://place.map.kakao.com/11186726
고려대학교 서울캠퍼스,수해복마라탕,중식,"정운오IT교양관 후문,자연계캠퍼스 후문",1,https://place.map.kakao.com/11186728
고려대학교 서울캠퍼스,한성양꼬치,중식,"정운오IT교양관 후문,자연계캠퍼스 후문",2,https://place.map.kakao.com/11186730
,,,,,
고려대학교 서울캠퍼스,지오파스타,이탈리안,법학관 입구,,https://place.map.kakao.com/12971217
고려대학교 서울캠퍼스,마사,양식,정경대학 입구,,https://place.map.kakao.com/11186718
고려대학교 서울캠퍼스,매스플레이트,이탈리안,정경대학 입구,,https://place.map.kakao.com/21469550
고려대학교 서울캠퍼스,신마라명장,중식,"정운오IT교양관 후문,자연계캠퍼스 후문",,https://place.map.kakao.com/11186731
"""

with open(r'c:\Ha_dahyeok\2026_NEXT_CONTEST\korea_univ_restaurants.csv', 'a', encoding='utf-8') as f:
    f.write(append_text)

