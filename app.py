import json
from flask import Flask, Response, jsonify, request
from flask_restful import reqparse, abort, Api, Resource
from py import dbconn
from py.config import auth
import jwt

import sys, io

#sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
#sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')






app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False



def on_json_loading_failed_return_dict(e):  
    return {}

# ============================================================================= #
# 주문접수
# ============================================================================= #



@app.route('/ordrcpt', methods=['POST'])
def ordrcpt():

    auth2 = request.headers.get('Authorization')

    if(auth2 != auth.key):
        return Response('Unauthorized', 401)

    params = request.get_json(silent=True)
    
    if(params == None):
        response = {
            "Code":400,
            "Message":"필수 입력 값이 부족하거나 요청형식이 올바르지 않습니다."
        }
        return jsonify(response) # return type => Json
    
    if(not 'DataList' in params):
        response = {
            "Code":400,
            "Message":"필수 입력 값이 부족하거나 없습니다."
        }
        return jsonify(response) # return type => Json
    
    DataList = params['DataList']
    FailList = []
    AllFail = True
    response = {
                "Code": 200,
                "Message":"Success"
                }
    
    for i in range(len(DataList)):
        DataListItem = DataList[i]

        if(('PackageNo' in DataListItem)):
            PackageNo = DataListItem['PackageNo']

            query = 'SELECT PackageNo, OrderStatus FROM tbl_Cellex_Data WHERE PackageNo = %s'
            result = dbconn.select_by_qNd(query, ((PackageNo)))
            print(result)


            # 유효한 입력 값
            if(('CountryCode' in DataListItem) and ('PackageNo' in DataListItem) and ('SellerName' in DataListItem) and 
                ('SellerPhoneNo' in DataListItem) and ('SellerAddress' in DataListItem) and ('ReceiverName' in DataListItem) and
                ('ReceiverPhoneNo1' in DataListItem) and ('ReceiverPostalcode' in DataListItem) and ('ReceiverDetailAddr' in DataListItem) and
                ('Currency' in DataListItem)  and ('ItemList' in DataListItem)):    

                CountryCode = DataListItem['CountryCode']
                PackageNo = DataListItem['PackageNo']
                SellerName = DataListItem['SellerName']
                SellerPhoneNo = DataListItem['SellerPhoneNo']
                SellerAddress = DataListItem['SellerAddress']
                ReceiverName = DataListItem['ReceiverName']
                ReceiverPhoneNo1 = DataListItem['ReceiverPhoneNo1']
                ReceiverPostalcode = DataListItem['ReceiverPostalcode']
                ReceiverDetailAddr = DataListItem['ReceiverDetailAddr']
                Currency = DataListItem['Currency']
                ItemList = str(DataListItem['ItemList'])

                OrderNo = ""
                ReceiverNameYomigana = ""
                ReceiverPhoneNo2 = ""      
                ReceiverState = ""
                ReceiverCity = ""     
                ReceiverEmail = ""
                DeliverMessage = ""
                RealWeight = ""

                if('OrderNo' in DataListItem):
                    OrderNo = DataListItem['OrderNo']
                if('ReceiverNameYomigana' in DataListItem):
                    ReceiverNameYomigana = DataListItem['ReceiverNameYomigana']
                if('ReceiverPhoneNo2' in DataListItem):
                    ReceiverPhoneNo2 = DataListItem['ReceiverPhoneNo2']   
                if('ReceiverState' in DataListItem):
                    ReceiverState = DataListItem['ReceiverState']
                if('ReceiverCity' in DataListItem):
                    ReceiverCity = DataListItem['ReceiverCity']  
                if('ReceiverEmail' in DataListItem):
                    ReceiverEmail = DataListItem['ReceiverEmail']
                if('DeliverMessage' in DataListItem):
                    DeliverMessage = DataListItem['DeliverMessage']
                if('RealWeight' in DataListItem):
                    RealWeight = DataListItem['RealWeight']

                # 등록되지 않은 PackageNo
                if(result == "null"):
                    query = "INSERT INTO tbl_Cellex_Data " \
                            "(CountryCode, PackageNo, OrderNo, SellerName, SellerPhoneNo ,SellerAddress, ReceiverName, ReceiverNameYomigana, ReceiverPhoneNo1, ReceiverPhoneNo2, " \
                            "ReceiverPostalcode, ReceiverState, ReceiverCity, ReceiverDetailAddr, ReceiverEmail, Currency, DeliverMessage, " \
                            "ItemList, RealWeight)" \
                            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" 

                    data = ((CountryCode, PackageNo, OrderNo, SellerName, SellerPhoneNo ,SellerAddress, ReceiverName, ReceiverNameYomigana, ReceiverPhoneNo1, ReceiverPhoneNo2,
                            ReceiverPostalcode, ReceiverState, ReceiverCity, ReceiverDetailAddr, ReceiverEmail, Currency, DeliverMessage,
                            ItemList, RealWeight))
                    
                    dbconn.db_else_by_q(query, data)


                    query = "INSERT INTO tbl_Cellex_Tracking (Status, StatusDesc, PackageNo) VALUES (%s, %s, %s)" 
                    data = ((10, "입고대기", PackageNo))
                    dbconn.db_else_by_q(query, data)

                    AllFail = False
                # 등록된 경우
                else:
                    # 주문 삭제 후 재등록하는 경우
                    if(result[0]['OrderStatus'] == 2):
                        query = "UPDATE tbl_Cellex_Data SET OrderStatus = 1, CountryCode = %s, PackageNo = %s, OrderNo = %s, SellerName = %s, SellerPhoneNo = %s, "\
                            "SellerAddress = %s, ReceiverName = %s, ReceiverNameYomigana = %s, ReceiverPhoneNo1 = %s, ReceiverPhoneNo2 = %s, " \
                            "ReceiverPostalcode = %s, ReceiverState = %s, ReceiverCity = %s, ReceiverDetailAddr = %s, ReceiverEmail = %s, Currency = %s, DeliverMessage = %s, " \
                            "ItemList = %s RealWeight = %s WHERE PackageNo = %s"
                        data = ((CountryCode, PackageNo, OrderNo, SellerName, SellerPhoneNo ,SellerAddress, ReceiverName, ReceiverNameYomigana, ReceiverPhoneNo1, ReceiverPhoneNo2,
                                ReceiverPostalcode, ReceiverState, ReceiverCity, ReceiverDetailAddr, ReceiverEmail, Currency, DeliverMessage,
                                ItemList, RealWeight, PackageNo))
                        dbconn.db_else_by_q(query, data)

                        query = "UPDATE tbl_Cellex_Tracking SET Status = 10, StatusDesc = '입고대기' WHERE PackageNo = %s"
                        dbconn.db_else_by_q(query, PackageNo)
                        AllFail = False
                    
                    else:
                        FailList.append({
                        "Code":400,
                        "PackageNo":PackageNo,
                        "Reason": "이미 등록된 PackageNo 입니다",
                        "Result": "Fail"
                        }) 
                        response['Code'] = 204
                        response['Message'] = "Partial Success"
                        response['FailList'] = FailList

            # 필수 입력 값 부족
            else: 
                FailList.append({
                                    "PackageNo":PackageNo,
                                    "Code": 400,
                                    "Result":"Fail",
                                    "Reason":"필수입력값이 없습니다."
                                })
                response['Code'] = 204
                response['Message'] = "Partial Success"
                response['FailList'] = FailList
        else:
            FailList.append({
                                "PackageNo":"None",
                                "Code": 400,
                                "Result":"Fail",
                                "Reason":"PackageNo는 필수 입력 값입니다."
                                })
            response['Code'] = 204
            response['Message'] = "Partial Success"
            response['FailList'] = FailList

    
    if(AllFail):
            response = {
                "Code": 400,
                "Message":"All Fail",
                "FailList":FailList
                }
    
    return jsonify(response) # return type => Json




# ============================================================================= #
# 접수조회
# ============================================================================= #

@app.route('/rcpt', methods=['POST'])
def rcpt():

    auth2 = request.headers.get('Authorization')

    if(auth2 != auth.key):
        return Response('Unauthorized', 401)
    
    params = request.get_json(silent=True)
    
    OrderList = []
    FailList = []
    response = {
            "Code": 200,
            "Message":"Success"
            }
    
    
    if(params == None):
        response = {
            "Code":400,
            "Message":"필수 입력 값이 부족하거나 요청형식이 올바르지 않습니다."        
            }
        return jsonify(response) # return type => Json
    
    if(not 'PackageNolist' in params):
            response = {
                "Code":400,
                "Message":"필수 입력 값이 부족하거나 없습니다."
            }
            return jsonify(response) # return type => Json
        

    PackageNolist = params['PackageNolist']
    
    
    

    AllFail = True
    for i in range(len(PackageNolist)):


        list_item = PackageNolist[i]

        

        query = '''SELECT CountryCode, PackageNo, OrderNo, SellerName, SellerPhoneNo ,SellerAddress, ReceiverName, ReceiverNameYomigana, ReceiverPhoneNo1, 
                ReceiverPhoneNo2, ReceiverCity, ReceiverDetailAddr, ReceiverEmail, Currency, DeliverMessage, 
                RealWeight, Width, Height, Depth, VolumeWeight, ChargedWeight, OrderStatus, ItemList, ReceiverPostalcode, ReceiverState FROM tbl_Cellex_Data WHERE PackageNo = %s'''

        result = dbconn.select_by_qNd(query, ((list_item)))

        if(result == "null" or result == None or result ==0 or result == "NULL" or result == ""):
            FailList.append({
                "Code":400,
                "PackageNo":list_item,
                "Reason": "미등록 PackageNo",
                "Result": "Fail"
            }) 

            response['Code'] = 204
            response['Message'] = "Partial Success"
            response['FailList'] = FailList
        else:
            AllFail = False
            if(result[0]['OrderStatus'] == 2):
                OrderList.append({"PackageNo":list_item,
                                "OrderStatus":"DELETE",
                                "StatusDesc":"주문삭제"
                                })
            else:   
                
                print(result[0])
                

                result[0].pop('OrderStatus')
                ItemList = str(result[0]['ItemList'])

                if(result[0]['ReceiverPhoneNo2'] == "\'\'" or result[0]['ReceiverPhoneNo2'] == "" or result[0]['ReceiverPhoneNo2'] == None):
                    result[0]['ReceiverPhoneNo2'] = None
                ItemList = ItemList.replace("\'", "\"")
                ItemList = ItemList.replace("None", "null")
                ItemList = json.loads(ItemList)
                result[0]['ItemList'] = ItemList
                
                
                
                
                
                OrderList.append(result[0])

            response['OrderList'] = OrderList
            
            
        

    if(AllFail):
            response = {
                "Code": 400,
                "Message":"All Fail",
                "FailList":FailList
                }
    
    

    return jsonify(response) # return type => Json



# ============================================================================= #
# 배송접수 사용X
# ============================================================================= #

@app.route('/delrcpt', methods=['POST'])
def delrcpt():

    auth2 = request.headers.get('Authorization')

    if(auth2 != auth.key):
        return Response('Unauthorized', 401)

    params = request.get_json(silent=True)

    if(params == None):
        response = {
            "Code":400,
            "Message":"DataList는 필수 입력 값입니다."
        }
        return jsonify(response) # return type => Json
    
    DataList = params['DataList']

    response = {
            "Code": 200,
            "Message":"All Success"
            }
    
    FailList = []
    AllFail = True
    for i in range(len(DataList)):
        DataListItem = DataList[i]

        
        if(('Status' in DataListItem) and ('StatusDesc' in DataListItem) and ('PackageNo' in DataListItem) and 
           ('LocalCompanyName' in DataListItem) and ('LocalInvoiceNo' in DataListItem) and ('TrackingList' in DataListItem)):    
        
            RegisterNo = ""

            if('RegisterNo' in DataListItem):
                RegisterNo = DataListItem['RegisterNo']
            
            Status = DataListItem['Status']
            StatusDesc = DataListItem['StatusDesc']
            PackageNo = DataListItem['PackageNo']
            LocalCompanyName = DataListItem['LocalCompanyName']
            LocalInvoiceNo = DataListItem['LocalInvoiceNo']
            TrackingList = str(DataListItem['TrackingList'])
    

            query = "INSERT INTO tbl_Cellex_Tracking " \
                "(RegisterNo, Status, StatusDesc, PackageNo, LocalCompanyName, LocalInvoiceNo, TrackingList)" \
                " VALUES (%s, %s, %s, %s, %s, %s, %s)" 


            data = ((RegisterNo, Status, StatusDesc, PackageNo, LocalCompanyName ,LocalInvoiceNo, TrackingList))
            
            dbconn.db_else_by_q(query, data)
            
            AllFail = False
        else:
            PackageNo = DataListItem['PackageNo']


            FailList.append({
                                "PackageNo":PackageNo,
                                "Code": 400,
                                "Result":"Fail",
                                "Reason":"필수입력값이 없습니다."
                            })
            response['Code'] = 204
            response['Message'] = "Partial Success"
            response['FailList'] = FailList

        if(AllFail):
            response = {
                "Code": 400,
                "Message":"All Fail",
                "FailList":FailList
                }
    
    

    
    
    return jsonify(response) # return type => Json




# ============================================================================= #
# 배송조회
# ============================================================================= #

@app.route('/delivery', methods=['POST'])
def delivery():

    auth2 = request.headers.get('Authorization')

    if(auth2 != auth.key):
        return Response('Unauthorized', 401)
    
    params = request.get_json(silent=True)

    if(params == None):
        response = {
            "Code":400,
            "Message":"필수 입력 값이 부족하거나 요청형식이 올바르지 않습니다."
        }
        return jsonify(response) # return type => Json
    
    if(not 'PackageNolist' in params):
        response = {
            "Code":400,
            "Message":"필수 입력 값이 부족하거나 없습니다."
        }
        return jsonify(response) # return type => Json
    
    
    PackageNolist = params['PackageNolist']
    
    query = "SELECT * FROM tbl_Cellex_Tracking WHERE PackageNo = %s"
    TrackList = []
    FailList = []

    response = {
            "Code": 200,
            "Message":"Success"
            }

    AllFail = True

    for i in range(len(PackageNolist)):
        list_item = PackageNolist[i]
        result = dbconn.select_by_qNd(query, ((list_item)))

        if(result == "null" or result == None or result ==0 or result == "NULL" or result == ""):
            FailList.append({
                "Code":400,
                "PackageNo":list_item,
                "Reason": "미등록 PackageNo",
                "Result": "Fail"
            }) 

            response['Code'] = 204
            response['Message'] = "Partial Success"
            response['FailList'] = FailList
        else:
            AllFail = False

            if(result[0]['Status'] == 0):
                TrackList.append({"PackageNo":list_item,
                                "Status":"DELETE",
                                "StatusDesc":"주문삭제"
                                })
            else:    
                TrackingList = str(result[0]['TrackingList'])
                TrackingList = TrackingList.replace("\'", "\"")
                TrackingList = TrackingList.replace("None", "null")
                TrackingList = json.loads(TrackingList)
                result[0]['TrackingList'] = TrackingList
                TrackList.append(result[0])
 
            response['TrackList'] = TrackList

    if(AllFail):
            response = {
                "Code": 400,
                "Message":"All Fail",
                "FailList":FailList
                }
            
    return jsonify(response) # return type => Json


# ============================================================================= #
# 데이터삭제
# ============================================================================= #

@app.route('/orddel', methods=['POST'])
def orddel():

    auth2 = request.headers.get('Authorization')

    if(auth2 != auth.key):
        return Response('Unauthorized', 401)
    
    params = request.get_json(silent=True)

    if(params == None):
        response = {
            "Code":400,
            "Message":"필수 입력 값이 부족하거나 요청형식이 올바르지 않습니다."
        }
        return jsonify(response) # return type => Json
    
    if(not 'PackageNolist' in params):
        response = {
            "Code":400,
            "Message":"필수 입력 값이 부족하거나 없습니다."
        }
        return jsonify(response) # return type => Json
    

    PackageNolist = params['PackageNolist']

    DeleteList = []
    FailList = []
    response = {
            "Code": 200,
            "Message":"All Success"
            }

    AllFail = True

    for i in range(len(PackageNolist)):
        list_item = PackageNolist[i]
        query = "SELECT Status, StatusDesc FROM tbl_Cellex_Tracking WHERE PackageNo = %s"
        result = dbconn.select_by_qNd(query, list_item)

        print(result)
        if(result == "null"):
            FailList.append({
                "Code":400,
                "PackageNo":list_item,
                "Reason": "미등록 PackageNo",
                "Result": "Fail"
            }) 

            response['Code'] = 204
            response['Message'] = "Partial Success"
            response['FailList'] = FailList

        elif(result[0]['Status'] == 10):
            #query = "UPDATE tbl_Cellex_Data SET OrderStatus = 2 WHERE PackageNo = %s"
            query = "DELETE FROM tbl_Cellex_Data WHERE PackageNo = %s"
            dbconn.db_else_by_q(query, list_item)

            #query = "UPDATE tbl_Cellex_Tracking SET Status = 0, StatusDesc = '주문삭제' WHERE PackageNo = %s"
            query = "DELETE FROM tbl_Cellex_Tracking WHERE PackageNo = %s"

            dbconn.db_else_by_q(query, list_item)

            DeleteList.append({
                                "PackageNo":list_item,
                                "Code": 200,
                                "Result":"Success"
                                })
            response['DeleteList'] = DeleteList
            AllFail = False
        elif(result[0]['Status'] == 0):
            FailList.append({
                                "PackageNo":list_item,
                                "Code": 400,
                                "Result":"Fail",
                                "Reason":"이미 삭제된 주문입니다."
                                })
            
            response['Code'] = 204
            response['Message'] = "Partial Success"
            response['FailList'] = FailList
        else:

            FailList.append({
                                "PackageNo":list_item,
                                "Code": 400,
                                "Result":"Fail",
                                "Reason":str(result[0]['StatusDesc']) + " 상태인 주문은 삭제가 불가능합니다"
                                })
            
            response['Code'] = 204
            response['Message'] = "Partial Success"
            response['FailList'] = FailList


    if(AllFail):
        response['Code'] = 400
        response['Message'] = "All Fail"
    
    return jsonify(response)


api = Api(app)

class reservchk(Resource):
    def get(self):
        json = {
            "id": auth.id,
            "password": auth.pw
        }
        encoded = jwt.encode(json, "secret", algorithm="HS256")
        return encoded, 200

api.add_resource(reservchk, '/auth')


class rchk(Resource):
    def get(self):
        return "ok", 200

api.add_resource(rchk, '/rcpts')




if __name__ == "__main__":
    app.run(debug=True, port=8123)