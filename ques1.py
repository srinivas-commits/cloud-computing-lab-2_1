from flask import Flask, jsonify, request, Response, render_template
from flask_restful import Api, Resource, reqparse, inputs, fields, marshal_with
import xml.etree.ElementTree as ET
import datetime, json

app = Flask(__name__)
api = Api(app)

class Record:
    def __init__(self, record_id, surname, name, datecreation):
        self.record_id = record_id
        self.surname = surname
        self.name = name
        self.datecreation = datecreation

class InMemoryRecordStore:
    def __init__(self):
        self.records = {}
        self.counter = 0
    
    def create(self, record):
        self.counter += 1
        record.record_id = self.counter
        self.records[self.counter] = record
        return record
    
    def get(self, record_id):
        return self.records.get(record_id)

record_fields = {
    'record_id': fields.Integer,
    'surname': fields.String,
    'name': fields.String,
    'datecreation': fields.DateTime
}

record_parser = reqparse.RequestParser()
record_parser.add_argument('surname', type=str, required=True, help='Surname cannot be blank')
record_parser.add_argument('name', type=str, required=True, help='Name cannot be blank')
record_parser.add_argument('date', type=str, required=False, help='Date cannot be blank')
record_store = InMemoryRecordStore()

class RecordController(Resource):
    @marshal_with(record_fields)
    def post(self):
        args = record_parser.parse_args()
        now = datetime.datetime.now()
        record = Record(None, args['surname'], args['name'], now)
        created_record = record_store.create(record)
        print(created_record)
        return created_record
    
    def get(self, record_id):
        record = record_store.get(record_id)
        if record:
            accept = request.headers.get('Accept')
            if accept == 'application/xml':
                record_xml = ET.Element('record')
                record_xml.set('id', str(record.record_id))
                surname_xml = ET.SubElement(record_xml, 'surname')
                surname_xml.text = record.surname
                name_xml = ET.SubElement(record_xml, 'name')
                name_xml.text = record.name
                datecreation_xml = ET.SubElement(record_xml, 'datecreation')
                datecreation_xml.text = str(record.datecreation.isoformat())
                response = Response(ET.tostring(record_xml), mimetype='application/xml')
            else:
                try:
                    result = {
                        "record_id": record.record_id,
                        "surname": record.surname,
                        "name": record.name,
                        "datecreation": record.datecreation.isoformat()
                    }
                    response = Response(json.dumps(result), mimetype='application/json')

                except Exception as e:
                    print(e)
                    print(record.record_id)
                    print(record.surname)
                    result = {
                        "error": "Internal server error"
                    }
                    response = json.dumps(result)
                    response.mimetype = 'application/json'

            return response
        else:
            return {'message': 'Record not found'}

api.add_resource(RecordController, '/record', '/record/<int:record_id>')

@app.route('/', methods=['GET'])
def home():
    return render_template('ques1_1.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)