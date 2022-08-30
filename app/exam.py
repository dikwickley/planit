import functools
import json
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

exam_blueprint = Blueprint('exam',__name__, url_prefix='/exam')

@exam_blueprint.route('/all', methods=['GET'])
def get_all_exam():
    if request.method == 'GET':
        print(request.values)

        return json.dumps({"msg" : "done"})