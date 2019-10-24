from http import HTTPStatus

from mock import Mock
from numpy import int32, float64

from src.dto import BoundingBox
from src.dto.face_prediction import FacePrediction


def test__when_recognize_endpoint_is_requested__then_returns_predictions(client, mocker):
    expected_result = [
        {'box': {"xmax": 50, "xmin": 60, "ymax": 70, "ymin": 80}, 'prediction': 'Joe Bloggs', 'probability': 0.9},
        {'box': {"xmax": 10, "xmin": 20, "ymax": 30, "ymin": 40}, 'prediction': 'Fred Bloggs', 'probability': 0.85},
        {'box': {"xmax": 15, "xmin": 25, "ymax": 35, "ymin": 45}, 'prediction': 'John Smith', 'probability': 0.91},
        {'box': {"xmax": 35, "xmin": 36, "ymax": 39, "ymin": 40}, 'prediction': 'Igor Shaw', 'probability': 0.89}
    ]
    ret_val = [
        FacePrediction(box=BoundingBox(xmax=int32(50), xmin=int32(60), ymax=int32(70), ymin=int32(80)),
                       prediction='Joe Bloggs', probability=float64(0.9)),
        FacePrediction(box=BoundingBox(xmax=int32(10), xmin=int32(20), ymax=int32(30), ymin=int32(40)),
                       prediction='Fred Bloggs', probability=float64(0.85)),
        FacePrediction(box=BoundingBox(xmax=int32(15), xmin=int32(25), ymax=int32(35), ymin=int32(45)),
                       prediction='John Smith', probability=float64(0.91)),
        FacePrediction(box=BoundingBox(xmax=int32(35), xmin=int32(36), ymax=int32(39), ymin=int32(40)),
                       prediction='Igor Shaw', probability=float64(0.89))
    ]
    img = object()
    imread_mock = mocker.patch('src.api.controller.imageio.imread', return_value=img)
    get_face_predictions_mock = mocker.patch('src.api.controller.get_face_predictions', return_value=ret_val)

    res = client.post('/recognize', data=dict(file=(b'', 'group-photo.jpg'), content_type='multipart/form-data'))

    assert res.status_code == HTTPStatus.OK, res.json
    assert imread_mock.call_args[0][0].filename == 'group-photo.jpg'
    assert get_face_predictions_mock.call_args[0][0] == img
    assert res.json['result'] == expected_result


def test__given_no_limit_value__when_recognize_endpoint_is_requested__then_uses_no_limit(client, mocker):
    mocker.patch('src.api.controller.imageio.imread')
    get_face_predictions_mock: Mock = mocker.patch('src.api.controller.get_face_predictions', return_value=[])

    res = client.post('/recognize')

    assert res.status_code == HTTPStatus.OK, res.json
    assert get_face_predictions_mock.call_args[0][1] == 0


def test__given_limit_value_0__when_recognize_endpoint_is_requested__then_uses_no_limit(client, mocker):
    mocker.patch('src.api.controller.imageio.imread')
    get_face_predictions_mock: Mock = mocker.patch('src.api.controller.get_face_predictions', return_value=[])

    res = client.post('/recognize?limit=0')

    assert res.status_code == HTTPStatus.OK, res.json
    assert get_face_predictions_mock.call_args[0][1] == 0


def test__given_limit_value_1__when_recognize_endpoint_is_requested__then_uses_limit_1(client, mocker):
    mocker.patch('src.api.controller.imageio.imread')
    get_face_predictions_mock: Mock = mocker.patch('src.api.controller.get_face_predictions', return_value=[])

    res = client.post('/recognize?limit=1')

    assert res.status_code == HTTPStatus.OK, res.json
    assert get_face_predictions_mock.call_args[0][1] == 1


def test__given_limit_value_minus_1__when_recognize_endpoint_is_requested__then_returns_400(client, mocker):
    mocker.patch('src.api.controller.imageio.imread')
    mocker.patch('src.api.controller.get_face_predictions')

    res = client.post('/recognize?limit=-1')

    assert res.status_code == HTTPStatus.BAD_REQUEST, res.json
    assert res.json['message'] == 'Limit value is invalid'


def test__given_limit_value_words__when_recognize_endpoint_is_requested__then_returns_400(client, mocker):
    mocker.patch('src.api.controller.imageio.imread')
    mocker.patch('src.api.controller.get_face_predictions')

    res = client.post('/recognize?limit=hello')

    assert res.status_code == HTTPStatus.BAD_REQUEST, res.json
    assert res.json['message'] == 'Limit format is invalid'
