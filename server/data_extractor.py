#!/usr/bin/env python3
from bs4 import BeautifulSoup
import bs4
import json
import logging

from requests import get
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--file", help="The file to parse, should be json with 'TableContent': html-data", type=str)
parser.add_argument("--url", help="The url to extract or parse")
parser.add_argument("--pagelimit", help="The last page to extract from IRI", type=int, default=199)
parser.add_argument("--outfile", help="The file to write the output to in JSON format", type=str)

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def GetTrainDataFromIndianRailInfo(page_index: int) -> str:
    request_url = f"https://indiarailinfo.com/trains/{page_index}?i=1&date=undefined&drev=undefined&arev=undefined&&kkk=1735461331528"
    logger.info(f"Requesting data from {request_url}")
    json_data = get(request_url).json()
    if json_data is None:
        return None
    if 'TableContent' in json_data:
        return json_data['TableContent']
    return None

def GetBodyFromJson(file: str) -> str:
    data = ""
    with open(file) as f:
        json_data = json.load(f)
        if 'TableContent' in json_data:
            data = json_data['TableContent']
        
    return data

def GetTrainInfoFromHtml(htmlData: str) -> dict:
    bs = BeautifulSoup(htmlData, "html.parser")
    content_header = ["train_number", "train_name", "train_type", "train_zone", "start_date", "end_date", "source", "source_time", "dest", "dest_time", "duration", "halts", "days", "classes", "distance", "speed", "return_train_number"]
    train_info = {}
    for possible_row in bs.children:
        if possible_row.div is None:
            continue

        all_divs = possible_row.children
        all_div_content = []
        for div in all_divs:
            if div is None or len(div.contents) == 0:
                continue
            if div.span is not None and len(div.span.contents) > 0:
                all_div_content.append(div.span.contents[0])
            elif div.table is not None:
                # Special handle the table case
                table = div.table
                table_rows = table.children
                WeeklyBinSchedule = ""
                for row in table_rows:
                    for td in row.contents:
                        WeeklyBinSchedule += "1" if td.contents[0].strip() !="" else "0"
                all_div_content.append(WeeklyBinSchedule)
            else:
                all_div_content.append(div.contents[0])
            
        row = possible_row.div
        train_number = ''.join(row.contents)
        train_info[train_number] = dict(zip(content_header, all_div_content))
        del train_info[train_number]["start_date"]
        del train_info[train_number]["end_date"]

    return train_info

def GetTrainInfoFromUrl(url: str) -> dict:
    pass
# with open("train_info_1.html") as f:
#     data = f.read()
# soup = BeautifulSoup(data, "html.parser")

if __name__ == '__main__':
    args = parser.parse_args()
    
    globalTrainData = {}

    if args.file:
        htmlData = GetBodyFromJson(args.file)
        allTrainData = GetTrainInfoFromHtml(htmlData)
    else:
        for idx in range(args.pagelimit):
            logger.info(f"Processing page {idx}")
            data = GetTrainInfoFromHtml(GetTrainDataFromIndianRailInfo(idx))
            globalTrainData.update(data)
    
    if args.outfile:
        with open(args.outfile, "w") as f:
            json.dump(globalTrainData, f)
    else:
        print(f"Read data for {len(globalTrainData.keys())} trains")