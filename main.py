# uvicorn main:app --reload

import json
import os
from typing import Optional
from fastapi import FastAPI
from distutils.util import subst_vars
from fastapi import Body
from pydantic import BaseModel
from urllib.parse import unquote
from urllib.parse import urlparse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import logging
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError
import requests
# Load environment variables from .env file
from dotenv import load_dotenv

class RawGames(BaseModel):
    suggests: str
    algo: int

class Neo4jConnection:

    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def query(self, query, parameters=None, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.__driver.session(database=db) if db is not None else self.__driver.session()
            response = list(session.run(query, parameters))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response

conn = Neo4jConnection(uri="neo4j+s://5212060a.databases.neo4j.io", user="neo4j",pwd="arlHD7oHu9bbXMB_0SZpkHH7mTR187haaLjdyN85xDE")
load_dotenv()

# Access environment variables
apiUrl = os.getenv("NODE_URL")


# apiUrl = read_settings()
origins = [
    "http://localhost",
    "http://localhost:8080",
    apiUrl,
]


utmeSubjectCodeFull = ['ABIO', 'ABIZ', 'ABR', 'ACHE', 'AECO', 'AEI', 'AEW',
'AFIA', 'AGEO', 'AGOV', 'AGR', 'ALIT', 'AMW', 'ANH', 'APHY', 'APM', 'ARA',
'ART', 'AUM', 'AUP', 'BAE', 'BAS', 'BBC', 'BDC', 'BED', 'BEE', 'BIO', 'BLC',
'BOK', 'BUM', 'CAJ', 'CAT', 'CCP', 'CER', 'CHH', 'CHM', 'CIE', 'COA', 'COM',
 'COS', 'CRK', 'CSC', 'DAP', 'DGP', 'DYB', 'ECO', 'EFI', 'EIM', 'ELE', 'ELS',
 'ENG', 'FAN', 'FAW', 'FCP', 'FIA', 'FIS', 'FMT', 'FOR', 'FRE', 'FUM', 'GAM',
  'GEO', 'GHL', 'GKA', 'GMW', 'GOV', 'GPM', 'GRA', 'GRD', 'GWW', 'HAU', 'HECO',
   'HEE', 'HES', 'HIS', 'HOM', 'IBI', 'IBM', 'ICT', 'IGB', 'IMW', 'INS', 'ISS',
'ITS', 'JEW', 'LEG', 'LET', 'LEW', 'LGM', 'LIT', 'LVB', 'MAC', 'MAR',
'MAW', 'MEC', 'MET', 'MGM', 'MIN', 'MTH', 'MUS', 'MVM', 'OFP', 'PAD', 'PCP',
'PHE', 'PHO', 'PHY', 'PIM', 'POA', 'PPF', 'RAC', 'RTE', 'SAL', 'SBC', 'SCU',
'SHO', 'SOS', 'STK', 'STM', 'TED', 'TOU', 'TTT', 'TYP', 'UPH', 'VBB', 'VIA', 'WAT',
 'WFE', 'WOG', 'YOR']

utmeSubjectCode= ['PHY','MTH','GOV', 'GEO','POA','FRE','HIS','IGB','LIT','AGR',
'Music','BIO','Home ECO','ART','CHM','CRK','COM','ISS','ECO','Yoruba']

scienceSub = ['AGR','BIO','CHM','GEO','PHY', 'MTH']
artSub = ['ART','FRE','HIS','IGB','LIT', 'GOV', 'CRK']
socialScSub = ['COM','ECO','GOV','Home ECO']
managementSc = ['POA']
selected0 = ['CRK','ECO','GOV']
selected1 = ['CRK','ECO','GOV','LIT', 'HIS']
selected2 = ['LIT', 'HIS', 'FRE', 'GEO', 'PHY', 'ECO', 'CRK'] # education management
selected3 = ['MTH','BIO', 'PHY','ECO','COM']
selected4 = ['MTH', 'PHY', 'CHM', 'ART', 'GEO', 'BIO', 'ECO']
selected5 = ['MTH', 'PHY', 'CHM', 'AGR', 'BIO', 'ECO']
selected6 = ['MTH', 'ECO', 'GOV', 'HIS', 'GEO', 'LIT', 'FRE', 'CRK', 'ISS']
selected7 = ['MTH', 'PHY', 'CHM','GEO', 'ECO', 'ART'] #
selected8 = ['MTH', 'PHY', 'CHM', 'ART', 'GEO', 'BIO', 'ECO','AGR']


physicsChemBio =   [1,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0]
physicsChemAgric = [1,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0]
bioChemMaths =     [0,1,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0]
bioMathsPhysics =  [1,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0]
ecoMathsPhysics =  [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0]
geoMathsPhysics =  [1,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

chemMathsPhysics = [1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0]
bioChemAgric =     [0,0,0,0,0,0,0,0,0,1,0,1,0,0,1,0,0,0,0,0]
bioAgricMaths =    [0,1,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0]
agricMathsPhysics =[1,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0]
agricMathsChem =   [0,1,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0]

mathsChemPhysics = [1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0]
mathsChemEco =     [0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0]
mathsChemGeo =     [0,1,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0]

ecoGovCrk =        [0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

course_dict = {


    'AGR':	'Agriculture',
    'ART':	'Art (Fine Art)',
    'BIO':	'Biology',
    'CHM':	'Chemistry',
    'COM':	'Commerce',
    'CRK':	'Christian Rel. Know',
    'ECO':	'Economics',
    'FRE':	'French',
    'GEO':	'Geography',
    'GOV':	'Government',
    'HIS':	'History',
    'Home ECO':	'Home Economics',
    'IGB':	'Igbo',
    'ISS':	'Islamic Studies',
    'LIT':	'Lit. in English',
    'MTH':	'Mathematics',
    'Music':	'Music',
    'PHY':	'Physics',
    'POA':	'Princ. of Account',
    'Yoruba':	'Yoruba',
    'COS': 'Computer Studies',
    'PHE':'Physical and Health Education'

}



@app.get("/")
async def root():
    return {"message": "Hello Suggester API"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}

@app.get("/api/status")
async def check_status():
    return {"message": f"Check status:: {apiUrl}"}

# score: int, department:str, sub1:str, sub2:str, sub3:str
@app.get("/api/suggest-departments2/{aNo}")
async def suggestDepartment2(aNo):
    # o = urlparse(subs)
    print("urlparse::", aNo)

    # print("urlpasrse::", score,department,sub1,sub2,sub3)
    # print(".....receiving subjects", json.dumps(o.path, indent=3, sort_keys=True))

    # subjects = json.loads(o.params)
    # print(".....receiving subjects", json.dumps(subs, indent=3, sort_keys=True))
    try:
        return {"combostatus": "2","suggest": "2"}
    except:
        return {"combostatus": 500,"suggest": []}



def grabSuggestDepartment(subjects):
    anArray = ['UTME']
    # my_dict ={"java":100, "python":112, "c":11}

    # list out keys and values separately
    key_list = list(course_dict.keys())
    val_list = list(course_dict.values())

    # print key with val 100
    # position = val_list.index(100)
    # print(key_list[position])
    anArray.append( key_list[val_list.index(subjects["sub1"])] )
    anArray.append( key_list[val_list.index(subjects["sub2"])] )
    anArray.append( key_list[val_list.index(subjects["sub3"])] )
    # print("VIEW ANARRAY", anArray)
    # anArray.append({i for i in course_dict if course_dict[i]== subjects.sub2}[0] )
    # anArray.append({i for i in course_dict if course_dict[i]== subjects.sub3}[0] )
    # print("ARRAY::", anArray)
    r1 = suggestCourses(anArray)
    return r1

# Suggest courses given jambNo, Sub1, Sub2, Sub3
def suggestCourses(anArrayList):
    courseArray = []
    suggestedCourse = []

    for i in range(len(utmeSubjectCode)):
        courseArray.append(0)
    for i in range(3):
        if (anArrayList[i+1] in utmeSubjectCode ):
            answer = utmeSubjectCode.index(anArrayList[i+1])
            courseArray[answer] = 1

    if (courseArray == physicsChemBio or courseArray == physicsChemAgric ):
        suggestedCourse.append('Agriculture Economics &Extension')
        suggestedCourse.append('Animal Science & Production')
        suggestedCourse.append('Crop Science & Horticulture')
        suggestedCourse.append('Fisheries and Aquaculture')
        suggestedCourse.append('Food Science & Technology')
        suggestedCourse.append('Forestry & Wildlife')
        suggestedCourse.append('Agriculture')
        suggestedCourse.append('Crop Science & Horticulture')
        suggestedCourse.append('Soil Science and Land Management')
        suggestedCourse.append('Education & Integrated Science')


    if (courseArray == geoMathsPhysics or courseArray == ecoMathsPhysics ):
        suggestedCourse.append('Computer Science')

    if (courseArray == mathsChemGeo or courseArray == mathsChemEco ):
        suggestedCourse.append('Mathematics')
        suggestedCourse.append('Pure And Industrial Chemistry')
        suggestedCourse.append('Chemistry')
        suggestedCourse.append('Science Education')


    # if (courseArray == JVar.mathsChemEco ):
    #     suggestedCourse.append('Statistics')

    # if (courseArray == JVar.ecoMathsPhysics ):
    #     suggestedCourse.append('Statistics')



    if(courseArray == physicsChemBio):
        suggestedCourse.append('Anatomy')
        suggestedCourse.append('Physiology')
        suggestedCourse.append('Applied Biochemistry')
        suggestedCourse.append('Biological Science(S)')
        suggestedCourse.append('Applied Microbiology & Brewing')
        suggestedCourse.append('Botany')
        suggestedCourse.append('Parasitology & Entomology')
        suggestedCourse.append('Zoology')
        suggestedCourse.append('Education & Biology')
        suggestedCourse.append('Science Education')
        suggestedCourse.append('Building & Woodwork Technology Education')
        suggestedCourse.append('Technical Education')
        suggestedCourse.append('Electrical/Electronics Education')
        suggestedCourse.append('Auto & Mechanical Technology Education')
        suggestedCourse.append('Radiography')
        suggestedCourse.append('Environmental Health Science')
        suggestedCourse.append('Nursing/Nursing Science')
        suggestedCourse.append('Medical Laboratory Science')
        suggestedCourse.append('Medical Rehabilitation')
        suggestedCourse.append('HUMAN NUTRITION & DIETETICS')
        suggestedCourse.append('Medicine & Surgery')
        suggestedCourse.append('Pharmacy')
        suggestedCourse.append('Pharm D')
        suggestedCourse.append('Geological Sciences')
        suggestedCourse.append('Geophysics')
        suggestedCourse.append('PHYSICS/INDUSTRIAL PHYSICS')
        suggestedCourse.append('Animal Science & Production')
        suggestedCourse.append('Soil Science and Land Management')






    if(courseArray == bioChemMaths):
        suggestedCourse.append('Applied Biochemistry')
        suggestedCourse.append('Parasitology & Entomology')
        suggestedCourse.append('Zoology')
        suggestedCourse.append('Education & Biology')
        suggestedCourse.append('Science Education')
        suggestedCourse.append('Biological Science(S)')
        suggestedCourse.append('Education & Integrated Science')
        suggestedCourse.append('Pure & Industrial Chemistry')
        suggestedCourse.append('Animal Science & Production')
        suggestedCourse.append('Soil Science and Land Management')
        suggestedCourse.append('Statistics')
        suggestedCourse.append('Pure And Industrial Chemistry')
        suggestedCourse.append('Chemistry')
        suggestedCourse.append('Agriculture Economics &Extension')
        suggestedCourse.append('Animal Science & Production')
        suggestedCourse.append('Crop Science & Horticulture')
        suggestedCourse.append('Fisheries and Aquaculture')
        suggestedCourse.append('Food Science & Technology')
        suggestedCourse.append('Forestry & Wildlife')
        suggestedCourse.append('Agriculture')
        suggestedCourse.append('Crop Science & Horticulture')
        suggestedCourse.append('Soil Science and Land Management')
        suggestedCourse.append('Education & Integrated Science')





    if(courseArray == bioChemAgric):
        suggestedCourse.append('Zoology')
        suggestedCourse.append('Education & Integrated Science')


    if(courseArray == bioMathsPhysics):
        suggestedCourse.append('Education & Biology')
        suggestedCourse.append('Education & Integrated Science')
        suggestedCourse.append('Education & Mathematics')
        suggestedCourse.append('Statistics')
        suggestedCourse.append('Computer Science')
        suggestedCourse.append('Electrical/Electronics Education')
        suggestedCourse.append('Education & Physics')



    if(courseArray == chemMathsPhysics):
        suggestedCourse.append('Education & Chemistry')
        suggestedCourse.append('Education & Integrated Science')
        suggestedCourse.append('Building & Woodwork Technology Education')
        suggestedCourse.append('Technical Education')

        suggestedCourse.append('Electrical/Electronics Education')
        suggestedCourse.append('Auto & Mechanical Technology Education')
        suggestedCourse.append('Agricultural & Bioresources Engineering')
        suggestedCourse.append('Chemical Engineering')
        suggestedCourse.append('Industrial Production Engineering')
        suggestedCourse.append('Mechanical Engineering')
        suggestedCourse.append('Metallurgical & Materials Engineering')
        suggestedCourse.append('Polymer & Textile Engineering')
        suggestedCourse.append('Electronics & Computer Engineering')
        suggestedCourse.append('Civil Engineering')
        suggestedCourse.append('Mathematics')
        suggestedCourse.append('Statistics')

        suggestedCourse.append('Electrical Engineering')
        suggestedCourse.append('Petroleum Engineering')
        suggestedCourse.append('Building')
        suggestedCourse.append('Geological Sciences')
        suggestedCourse.append('Geophysics')
        suggestedCourse.append('PHYSICS/INDUSTRIAL PHYSICS')
        suggestedCourse.append('Computer Science')
        suggestedCourse.append('Education & Computer Science')
        suggestedCourse.append('Education & Mathematics')
        suggestedCourse.append('Pure And Industrial Chemistry')
        suggestedCourse.append('Chemistry')




    if(courseArray == agricMathsPhysics):
        suggestedCourse.append('Education & Integrated Science')
        suggestedCourse.append('Electrical/Electronics Education')
        suggestedCourse.append('Statistics')




    if(courseArray == agricMathsChem):
        suggestedCourse.append('Education & Integrated Science')
        suggestedCourse.append('Education & Chemistry')
        suggestedCourse.append('Pure & Industrial Chemistry')
        suggestedCourse.append('Animal Science & Production')
        suggestedCourse.append('Soil Science and Land Management')
        suggestedCourse.append('Statistics')
        suggestedCourse.append('Chemistry')
        suggestedCourse.append('Agriculture Economics &Extension')
        suggestedCourse.append('Animal Science & Production')
        suggestedCourse.append('Crop Science & Horticulture')
        suggestedCourse.append('Fisheries and Aquaculture')
        suggestedCourse.append('Food Science & Technology')
        suggestedCourse.append('Forestry & Wildlife')
        suggestedCourse.append('Agriculture')
        suggestedCourse.append('Crop Science & Horticulture')
        suggestedCourse.append('Soil Science and Land Management')
        suggestedCourse.append('Education & Integrated Science')



    if(courseArray == ecoGovCrk):
        suggestedCourse.append('Information Management')



    if(courseArray == bioAgricMaths):
        suggestedCourse.append('Education & Integrated Science')
        suggestedCourse.append('Statistics')


    # the any three subjects people
    suggestedCourse.append('Chinese Studies')
    suggestedCourse.append('Fine/Applied Arts')
    suggestedCourse.append('Philosophy')
    suggestedCourse.append('Early Childhood & Primary Education')
    suggestedCourse.append('Guidance & Counselling')
    suggestedCourse.append('Guidance and Counseling- Health option')
    suggestedCourse.append('Guidance and Counseling- Biology option')
    suggestedCourse.append('Adult Education')
    suggestedCourse.append('Educational Management & Policy')
    suggestedCourse.append('Library & Information Management')
    suggestedCourse.append('Educational Foundations')
    suggestedCourse.append('Sociology')









    newList = socialScSub + artSub # concatenate arts and social sciences list
    newList2 = socialScSub + scienceSub #concatenate social and science list
    newList3 = selected4 + scienceSub
    answer = [1,1,1]
    temp = [0,0,0]
    # print('NEWLIST2', newList2)
    for i in range(3):
        if (anArrayList[i+1] in newList2 ):
            temp[i] = 1
    if (answer == temp):
        # print("INSIDE SCIENCE ED")
        suggestedCourse.append('Science Education')


    # temp = [0,0,0]
    # for i in range(3):
    #     if (anArrayList[i+1] in selected0 ):
    #         temp[i] = 1
    # if (answer == temp):
    #     suggestedCourse.append('Library & Information Management')


    temp = [0,0,0]
    for i in range(3):
        if (anArrayList[i+1] in newList ):
            # answer = utmeSubjectCode.index(anArrayList[i+1])
            temp[i] = 1
    if (answer == temp):
        suggestedCourse.append('Education & Igbo')
        suggestedCourse.append('African & Asian Studies')
        suggestedCourse.append('Linguistics')
        suggestedCourse.append('Modern & European Languages')

        suggestedCourse.append('Civil Law')
        if ('HIS' in anArrayList) or ('GOV' in anArrayList):
            suggestedCourse.append('History')


    if ('BIO' in anArrayList):
        temp = [0,0,0]
        for i in range(3):
            if (anArrayList[i+1] in newList2 or anArrayList[i+1] == 'PHE'):
                # answer = JVar.utmeSubjectCode.index(anArrayList[i+1])
                temp[i] = 1
        if (answer == temp):
            suggestedCourse.append('Human Kinetics')
            suggestedCourse.append('Health Education')
            suggestedCourse.append('Physical Education')
            suggestedCourse.append('Physical & Health Education')
        temp = [0,0,0]
        for i in range(3):
            if (anArrayList[i+1] in utmeSubjectCode ):
                temp[i] = 1
        if (answer == temp):
            suggestedCourse.append('Psychology')

    if ('GEO' in anArrayList):
        temp = [0,0,0]
        for i in range(3):
            if (anArrayList[i+1] in newList3 ):
                temp[i] = 1
        if (answer == temp):
            suggestedCourse.append('Geography & Meteorology')



    if ('PHY' in anArrayList and ('MTH' in anArrayList or 'CHM' in anArrayList) ):
            temp = [0,0,0]
            for i in range(3):
                if (anArrayList[i+1] in newList2 ):
                    # answer = utmeSubjectCode.index(anArrayList[i+1])
                    temp[i] = 1
            if (answer == temp and not ('MTH' in anArrayList and 'CHM' in anArrayList)):
                suggestedCourse.append('Physics')
                suggestedCourse.append('Education & Physics')


    # a selection
    # temp = [0,0,0]
    # for i in range(3):
    #     if (anArrayList[i+1] in selected1 ):
    #         temp[i] = 1
    # if (answer == temp):
    #     suggestedCourse.append('Adult Education')
        # suggestedCourse.append('Adult and Continuing Education-Accounting Option')
        # suggestedCourse.append('Adult and Continuing Education-Economics Option')
        # suggestedCourse.append('Adult and Continuing Education-Marketing Option')
        # suggestedCourse.append('Adult and Continuing Education-Mass Communication Option')
        # suggestedCourse.append('Adult and Continuing Education-Political Science Option')

        # suggestedCourse.append('Adult and Continuing Education-Accounting Option')


    temp = [0,0,0]
    for i in range(3):
        if (anArrayList[i+1] in selected2 or anArrayList[i+1] in selected1):
            temp[i] = 1
    if (answer == temp):
        suggestedCourse.append('Educational Management-Science Option')
        suggestedCourse.append('Educational Management-Arts Option')
        suggestedCourse.append('Educational Management-Social/Environmental Option')
        suggestedCourse.append('Educational Management-Management Option')
        # suggestedCourse.append('Educational Management & Policy')

        suggestedCourse.append('Education & English Language')
        suggestedCourse.append('Education & Religious Studies')
        suggestedCourse.append('Education & History')
        suggestedCourse.append('Education & Political Science')
        suggestedCourse.append('Education & Geography')
        # suggestedCourse.append('Education & Accountancy')
        suggestedCourse.append('Education & Accounting')

        suggestedCourse.append('Education & Music')
        suggestedCourse.append('Education & Igbo')






    if ('MTH' in anArrayList):
        temp = [0,0,0]
        for i in range(3):
            if (anArrayList[i+1] in selected3 ):
                temp[i] = 1
        if (answer == temp):
            suggestedCourse.append('Education & Computer Science')
            suggestedCourse.append('Education & Mathematics')
        # temp = [0,0,0]
        for i in range(3):
            if (anArrayList[i+1] in socialScSub ):
                suggestedCourse.append('Accounting')
                break



        temp = [0,0,0]
        for i in range(3):
            if (anArrayList[i+1] in selected5 ):
                temp[i] = 1
        if (answer == temp):
            suggestedCourse.append('Statistics')
            suggestedCourse.append('Environmental Management')



        if ('PHY' in anArrayList):
            temp = [0,0,0]
            for i in range(3):
                if (anArrayList[i+1] in selected4 ):
                    temp[i] = 1
            if (answer == temp):
                suggestedCourse.append('Architecture')
            if ('COS' in anArrayList):
                suggestedCourse.append('Computer Science')
                suggestedCourse.append('Education & Computer Science')
            temp = [0,0,0]
            for i in range(3):
                if (anArrayList[i+1] in scienceSub ):
                    temp[i] = 1
            if (answer == temp):
                suggestedCourse.append('Education & Physics')
                suggestedCourse.append('Computer Science')




            temp = [0,0,0]
            for i in range(3):
                if (anArrayList[i+1] in selected8 ):
                    temp[i] = 1
            if (answer == temp):
                suggestedCourse.append('Quantity Surveying')
                suggestedCourse.append('Surveying & Geoinformatics')



        if ('ECO' in anArrayList):
            temp = [0,0,0]
            for i in range(3):
                if (anArrayList[i+1] in utmeSubjectCode ):
                    temp[i] = 1
            if (answer == temp):
                suggestedCourse.append('Business Education')
                suggestedCourse.append('Business Administration')
                suggestedCourse.append('Marketing')
                suggestedCourse.append('Education & Economics')

                suggestedCourse.append('Estate Management')
                suggestedCourse.append('Cooperative Economics & Management')
                suggestedCourse.append('Entrepreneurship')


            temp = [0,0,0]
            for i in range(3):
                if (anArrayList[i+1] in selected6 ):
                    temp[i] = 1
            if (answer == temp):
                suggestedCourse.append('Economics')
            for i in range(3):
                if (anArrayList[i+1] in newList):
                    temp[i] = 1
            if (answer == temp):
                suggestedCourse.append('Banking & Finance')
            if ('POA' in anArrayList):
                suggestedCourse.append('Banking & Finance')



            # temp = [0,0,0]
            # for i in range(3):
            #     if (anArrayList[i+1] in newList ):
            #         temp[i] = 1
            # if (answer == temp):
            #     suggestedCourse.append('Banking & Finance')





    if (('GOV' in anArrayList) or ('HIS' in anArrayList) ):
        temp = [0,0,0]
        for i in range(3):
            if (anArrayList[i+1] in newList ):
                temp[i] = 1
        # print('inside4Pol::', temp, not ('GOV' in anArrayList and 'HIS' in anArrayList), answer == temp)
        if (answer == temp and  not ('GOV' in anArrayList and 'HIS' in anArrayList)):

            suggestedCourse.append('Education & Political Science')
            suggestedCourse.append('Political Science')
        elif (answer == temp):
            print('inside elif')

            suggestedCourse.append('English Language & Literature')







    # literature and two others
    # tempArt = artSub # make a copy of arts subject
    if ('LIT' in anArrayList):
        answer = [1,1,1]
        temp = [0,0,0]
        for i in range(3):
            if (anArrayList[i+1] in artSub ):
                temp[i] = 1
        if (answer == temp):
            suggestedCourse.append('English Language & Literature')
        socialCount = 0
        for i in range(3):
            if (anArrayList[i+1] in socialScSub ):
                socialCount += 1
                temp[i] = 1
        if (answer == temp and socialCount == 1):
            suggestedCourse.append('English Language & Literature')

        temp = [0,0,0]
        for i in range(3):
            if (anArrayList[i+1] in newList ):
                temp[i] = 1
        if (answer == temp):
            suggestedCourse.append('Theatre Arts')
            suggestedCourse.append('Mass Communication')
            suggestedCourse.append('Education English')


    # one art subject and any other two subjects
    tempMarker = False
    for i in range(3):
        if (anArrayList[i+1] in artSub ):
                tempMarker = True
        if (tempMarker):
            suggestedCourse.append('Music')
            suggestedCourse.append('Religious & Human Relations')

    if ('HIS' in anArrayList):
        temp = [0,0,0]
        for i in range(3):
            if (anArrayList[i+1] in newList ):
                temp[i] = 1
        if (answer == temp):
            suggestedCourse.append('Education & History')

    if ('FRE' in anArrayList):
        temp = [0,0,0]
        for i in range(3):
            if (anArrayList[i+1] in newList ):
                temp[i] = 1
        if (answer == temp):
            suggestedCourse.append('French')
            suggestedCourse.append('Education & French')

    if ('CRK' in anArrayList or 'ISS' in anArrayList):
        temp = [0,0,0]
        for i in range(3):
            if (anArrayList[i+1] in utmeSubjectCode ):
                temp[i] = 1
        if (answer == temp):
            suggestedCourse.append('Education & Religious Studies')

    if ('ECO' in anArrayList):
        temp = [0,0,0]
        for i in range(3):
            if (anArrayList[i+1] in newList ):
                temp[i] = 1
        if (answer == temp):
            suggestedCourse.append('Education & Economics')

    if ('IGB' in anArrayList):
        temp = [0,0,0]
        for i in range(3):
            if (anArrayList[i+1] in utmeSubjectCode ):
                temp[i] = 1
        if (answer == temp):
            suggestedCourse.append('Education & Igbo')
    if ('ART' in anArrayList):
        temp = [0,0,0]
        for i in range(3):
            if (anArrayList[i+1] in utmeSubjectCode ):
                temp[i] = 1
        if (answer == temp):
            suggestedCourse.append('Education Fine& Applied Art')

    if ('Music' in anArrayList):
        temp = [0,0,0]
        for i in range(3):
            if (anArrayList[i+1] in utmeSubjectCode ):
                temp[i] = 1
        if (answer == temp):
            suggestedCourse.append('Education Music')

    if ('GOV' in anArrayList and 'ECO' in anArrayList):
        suggestedCourse.append('Public Administration')


    if ('CHM' in anArrayList):
        temp = [0,0,0]
        for i in range(3):
            if (anArrayList[i+1] in utmeSubjectCode ):
                temp[i] = 1
        if (answer == temp):
            suggestedCourse.append('AGRICULTURAL SCIENCE &amp; EDUCATION')
            suggestedCourse.append('HOME ECONOMICS &amp; EDUCATION')

    # CourseList = []
    return unique(suggestedCourse)


def getCoursesCutOffList():

    url = apiUrl + '/api/check-depts-cutoff'
    response = requests.get(url)
    print(".....querying DB for courses cutoff")

    # print("courses data", response.status_code, response.json())
    return response.json()["data"]

def unique(list1):

    # initialize a null list
    unique_list = []

    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    unique_list.sort()
    return unique_list


# this api receives subject combination and suggests courses that the person is eligible for
@app.get("/api/suggest-departments/{subs}")
async def suggestDepartment(subs):
    # o = urlparse(subs)
    # print("urlpasrse::", o.path)
    # print("urlpasrse::", subs)
    # print("urlpasrse::", subs)
    # print("URLPARSE", o)
    subjects = json.loads(subs)
    print(".....receiving subjects")
    score = subjects["score"]
    department  = unquote(subjects["department"])
    suggestions = grabSuggestDepartment(subjects)
    r1 = getCoursesCutOffList()

    print(".....receiving suggestions(d,S)", unquote(department), score)
    # print(".....receiving suggestions",  suggestions)
    refined_suggestions = []

    comboOK = 202

    print(".....refining suggestions")
    for prelim_options in suggestions:
        for dept_cutoff in r1:
            # print("dept_cutoff:::",dept_cutoff)
            cutoffinfo = dept_cutoff
            # cutoffinfo = json.loads(dept_cutoff)
            # print("cuttoffinfo", cutoffinfo["department"].lower())
            if cutoffinfo["department"].lower() == prelim_options.lower() and int(score) >= cutoffinfo["utme_cutoff"]:
                if (prelim_options.lower() == department.lower()):
                    comboOK = 200
                    break
                refined_suggestions.append(prelim_options)
    # if department in refined_suggestions:
    #     comboOK = 200
    # refined_suggestions2 = refined_suggestions.sort()
    print("refined suggestions::")



    try:
        return {"combostatus": comboOK,"suggest": refined_suggestions}
    except:
        return {"combostatus": 500,"suggest": []}


# this api receives subject combination and suggests courses that the person is eligible for
@app.get("/api/suggest-department-without-depcutoff")
async def suggestDepartment2(subs):
    subjects = json.loads(subs)
    print(".....receiving subjects")
    score = subjects["score"]
    suggestions = grabSuggestDepartment(subjects)
    # r1 = getCoursesCutOffList()

    print(".....receiving suggestions")
    refined_suggestions = []

    comboOK = 202

    # print(".....refining suggestions")
    # for prelim_options in suggestions:
    #     for dept_cutoff in r1:
    #         cutoffinfo = dept_cutoff
    #         if cutoffinfo["department"] == prelim_options and int(score) >= cutoffinfo["utme_cutoff"]:
    #             refined_suggestions.append(prelim_options)
    # print("refined suggestions::", refined_suggestions)
    try:
        return {"combostatus": comboOK,"suggest": suggestions}
    except:
        return {"combostatus": 500,"suggest": []}

async def save2Neo4jRawGames(dataF, Algo):
    # Aura queries use an encrypted connection using the "neo4j+s" URI scheme
    try:
        await add_raw_games(Algo,dataF)
        time.sleep( 5.0)
        return True

    except:
        return False



    # update_games(dataF)


async def add_raw_games(Algo, rows, batch_size=5000):
       # Adds paper nodes and (:Author)--(:Paper) and
   # (:Paper)--(:Category) relationships to the Neo4j graph as a
   # batch job.
   query = '''
   UNWIND $rows as row

    WITH row
Merge (l:BetDate{datePosted:date()}) with row,l
Merge (al:Algorithm{algo:$Algo})<-[:ALGO_USED]-(l)
WITH row, al, l
   Merge (g:RawGames{team:row.team, bet:row.bet,typ_of_bet: row.typ_of_bet})-[:BET_FOR_THIS_DAY{betDate:l.datePosted}]->(al)



   RETURN count(distinct g) as total
   '''

#    print('query::', query)
   return await insert_data(query, rows, batch_size, Algo)


async def insert_data(query, rows, batch_size = 10000, Algo = 3):
    # Function to handle the updating the Neo4j database in batch mode.

    total = 0
    batch = 0
    start = time.time()
    result = None

    while batch * batch_size < len(rows):

        res = conn.query(query,
                         parameters = {'rows': rows[batch*batch_size:(batch+1)*batch_size].to_dict('records'), 'Algo': Algo})
        total += res[0]['total']
        batch += 1
        result = {"total":total,
                  "batches":batch,
                  "time":time.time()-start}
        print(result)

    return result



# set raw games
@app.post("/api/set-raw-games/")
async def setRawGames(betTotal0: RawGames):
# def saveTotalGen(betTotal=[]):
    print(betTotal0)
    answer = False
#     betTotal = json.loads(betTotal0)
#     suggests = betTotal[suggests]
#     algo = betTotal[algo]
    suggests = betTotal.suggests
    algo = betTotal.algo

    df = pd.DataFrame(suggests)
    try:
        answer = await save2Neo4jRawGames(df, algo)
    except:
        print('ERROR UPLOADING raw bets suggestions')
        pass
    try:
        return {"status": 200, "message": "success"}
    except:
        return {"status": 500,"message": "error"}

# korotebets login api
@app.get("/api/get-current-games")
async def getCurrentGames():
    bname = 'edu'
    query_string = ''' MATCH (n:BetDate)-[]-(al:Algorithm)-[]-(r:RawGames)
    where n.datePosted = date() return r as rawGames, al.algo as Algo
    '''
    gameList = []
    print('query::', query_string)
    result = conn.query(query_string, {"bname" : bname})
    # print('result::', result)
    try:
        for record in result:
#             print(record)
            gameList.append(record)
#             print(record['rawGames'])
#             print(record['rawGames']['properties'])

    except:
        print("ERROR@Get-Current-Games")

    try:
        return {"status": 200, "gameList": gameList}
    except:
        return {"status": 500,"gameList": []}




# @app.get("/api/save-vetted-games")
# async def saveVettedGames(subs):


