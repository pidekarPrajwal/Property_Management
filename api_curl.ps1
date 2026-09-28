# Property Management API curls.
# Copy one block into Git Bash or cmd. Do not run this file with PowerShell.
# Base URL: http://127.0.0.1:8000
# Login first, then replace <access_token> with the access value from the login response.
# Fixed CMD login: username admin, password 123456


1) api_name : auth/login ( POST )
curl --location 'http://127.0.0.1:8000/api/auth/login/' \
--header 'Content-Type: application/json' \
--data '{
    "username": "admin",
    "password": "123456"
}'

response
{
    "access": "<access_token>",
    "refresh": "<refresh_token>",
    "user": {
        "id": 1,
        "username": "admin",
        "first_name": "Admin",
        "last_name": "User",
        "email": "admin@example.com",
        "mobile_number": "1234567890",
        "designation": "CMD",
        "designation_label": "CMD",
        "state": null,
        "state_name": null,
        "region": null,
        "region_name": null,
        "district": null,
        "district_name": null,
        "area": null,
        "area_name": null,
        "project": null,
        "project_name": null,
        "is_active": true,
        "created_at": "2026-09-28T05:00:00.000000Z",
        "updated_at": "2026-09-28T05:00:00.000000Z"
    }
}


2) api_name : auth/refresh ( POST )
curl --location 'http://127.0.0.1:8000/api/auth/refresh/' \
--header 'Content-Type: application/json' \
--data '{
    "refresh": "<refresh_token>"
}'

response
{
    "access": "<access_token>"
}


3) api_name : auth/logout ( POST )
curl --location 'http://127.0.0.1:8000/api/auth/logout/' \
--header 'Authorization: Bearer <access_token>' \
--header 'Content-Type: application/json' \
--data '{
    "refresh": "<refresh_token>"
}'

response
{
    "detail": "Logged out successfully."
}


4) api_name : dashboard ( GET )
curl --location 'http://127.0.0.1:8000/api/dashboard/' \
--header 'accept: */*' \
--header 'Authorization: Bearer <access_token>'

No designation filter returns everything this account can see.
State head filter: ?designation=STATE_HEAD
Same idea for REGION_HEAD, DISTRICT_HEAD, AREA_HEAD, PROJECT_HEAD, CMD, MAIN_ADMIN.

curl --location 'http://127.0.0.1:8000/api/dashboard/?designation=STATE_HEAD' \
--header 'accept: */*' \
--header 'Authorization: Bearer <access_token>'

response
{
    "user": {
        "id": 6,
        "username": "pune_area_head",
        "first_name": "Neha",
        "last_name": "Kulkarni",
        "email": "neha.area@example.com",
        "mobile_number": "9000000006",
        "designation": "AREA_HEAD",
        "designation_label": "Area Head",
        "state": 1,
        "state_name": "Maharashtra",
        "region": 1,
        "region_name": "Pune",
        "district": 1,
        "district_name": "Pune",
        "area": 1,
        "area_name": "Pune Area",
        "project": null,
        "project_name": null,
        "is_active": true,
        "created_at": "2026-09-28T05:10:00.000000Z",
        "updated_at": "2026-09-28T05:10:00.000000Z"
    },
    "counts": {
        "users": 3,
        "states": 1,
        "regions": 1,
        "districts": 1,
        "areas": 1,
        "projects": 2,
        "sites": 1
    },
    "users": [],
    "states": [],
    "regions": [],
    "districts": [],
    "areas": [],
    "projects": [],
    "sites": [
        {
            "id": 1,
            "name": "Shivaji Nagar Site",
            "code": "SN",
            "address": "Shivaji Nagar, Pune",
            "latitude": "18.5308230",
            "longitude": "73.8474660",
            "area": 1,
            "area_name": "Pune Area",
            "project": 1,
            "project_name": "Pune Housing",
            "district": 1,
            "district_name": "Pune",
            "region": 1,
            "region_name": "Pune",
            "state": 1,
            "state_name": "Maharashtra",
            "is_active": true,
            "created_by": 6,
            "created_by_username": "pune_area_head",
            "created_at": "2026-09-28T05:20:00.000000Z",
            "updated_at": "2026-09-28T05:20:00.000000Z"
        }
    ]
}


5) api_name : state/add-state ( POST )
curl --location 'http://127.0.0.1:8000/api/add-state/' \
--header 'Authorization: Bearer <access_token>' \
--header 'Content-Type: application/json' \
--data '{
    "name": "Maharashtra",
    "code": "MH"
}'

response
{
    "id": 1,
    "name": "Maharashtra",
    "code": "MH",
    "created_at": "2026-09-28T05:01:00.000000Z",
    "updated_at": "2026-09-28T05:01:00.000000Z"
}


6) api_name : state/get-states ( GET )
curl --location 'http://127.0.0.1:8000/api/get-states/' \
--header 'Authorization: Bearer <access_token>'

response
[
    {
        "id": 1,
        "name": "Maharashtra",
        "code": "MH",
        "created_at": "2026-09-28T05:01:00.000000Z",
        "updated_at": "2026-09-28T05:01:00.000000Z"
    }
]


7) api_name : state/get-state-by-id ( GET )
curl --location 'http://127.0.0.1:8000/api/get-state-by-id/?id=1' \
--header 'Authorization: Bearer <access_token>'

response
{
    "id": 1,
    "name": "Maharashtra",
    "code": "MH",
    "created_at": "2026-09-28T05:01:00.000000Z",
    "updated_at": "2026-09-28T05:01:00.000000Z"
}


8) api_name : state/update-state ( PATCH )
curl --location --request PATCH 'http://127.0.0.1:8000/api/update-state/?id=1' \
--header 'Authorization: Bearer <access_token>' \
--header 'Content-Type: application/json' \
--data '{
    "code": "MH"
}'

response
{
    "id": 1,
    "name": "Maharashtra",
    "code": "MH",
    "created_at": "2026-09-28T05:01:00.000000Z",
    "updated_at": "2026-09-28T05:02:00.000000Z"
}


9) api_name : state/delete-state ( DELETE )
curl --location --request DELETE 'http://127.0.0.1:8000/api/delete-state/?id=2' \
--header 'Authorization: Bearer <access_token>'

response
{}


10) api_name : region/add-region ( POST )
curl --location 'http://127.0.0.1:8000/api/add-region/' \
--header 'Authorization: Bearer <access_token>' \
--header 'Content-Type: application/json' \
--data '{
    "name": "Pune",
    "code": "PN",
    "state": 1
}'

response
{
    "id": 1,
    "name": "Pune",
    "code": "PN",
    "state": 1,
    "state_name": "Maharashtra",
    "created_at": "2026-09-28T05:03:00.000000Z",
    "updated_at": "2026-09-28T05:03:00.000000Z"
}


11) api_name : region/get-regions ( GET )
curl --location 'http://127.0.0.1:8000/api/get-regions/?state=1' \
--header 'Authorization: Bearer <access_token>'

response
[
    {
        "id": 1,
        "name": "Pune",
        "code": "PN",
        "state": 1,
        "state_name": "Maharashtra",
        "created_at": "2026-09-28T05:03:00.000000Z",
        "updated_at": "2026-09-28T05:03:00.000000Z"
    }
]


12) api_name : region/get-region-by-id ( GET )
curl --location 'http://127.0.0.1:8000/api/get-region-by-id/?id=1' \
--header 'Authorization: Bearer <access_token>'

response
{
    "id": 1,
    "name": "Pune",
    "code": "PN",
    "state": 1,
    "state_name": "Maharashtra",
    "created_at": "2026-09-28T05:03:00.000000Z",
    "updated_at": "2026-09-28T05:03:00.000000Z"
}


13) api_name : region/update-region ( PATCH )
curl --location --request PATCH 'http://127.0.0.1:8000/api/update-region/?id=1' \
--header 'Authorization: Bearer <access_token>' \
--header 'Content-Type: application/json' \
--data '{
    "code": "PN"
}'

response
{
    "id": 1,
    "name": "Pune",
    "code": "PN",
    "state": 1,
    "state_name": "Maharashtra",
    "created_at": "2026-09-28T05:03:00.000000Z",
    "updated_at": "2026-09-28T05:04:00.000000Z"
}


14) api_name : region/delete-region ( DELETE )
curl --location --request DELETE 'http://127.0.0.1:8000/api/delete-region/?id=1' \
--header 'Authorization: Bearer <access_token>'

response
{}


15) api_name : district/add-district ( POST )
curl --location 'http://127.0.0.1:8000/api/add-district/' \
--header 'Authorization: Bearer <access_token>' \
--header 'Content-Type: application/json' \
--data '{
    "name": "Pune",
    "code": "PUN",
    "region": 1
}'

response
{
    "id": 1,
    "name": "Pune",
    "code": "PUN",
    "region": 1,
    "region_name": "Pune",
    "state": 1,
    "state_name": "Maharashtra",
    "created_at": "2026-09-28T05:05:00.000000Z",
    "updated_at": "2026-09-28T05:05:00.000000Z"
}


16) api_name : district/get-districts ( GET )
curl --location 'http://127.0.0.1:8000/api/get-districts/?region=1' \
--header 'Authorization: Bearer <access_token>'

response
[
    {
        "id": 1,
        "name": "Pune",
        "code": "PUN",
        "region": 1,
        "region_name": "Pune",
        "state": 1,
        "state_name": "Maharashtra",
        "created_at": "2026-09-28T05:05:00.000000Z",
        "updated_at": "2026-09-28T05:05:00.000000Z"
    }
]


17) api_name : district/get-district-by-id ( GET )
curl --location 'http://127.0.0.1:8000/api/get-district-by-id/?id=1' \
--header 'Authorization: Bearer <access_token>'

response
{
    "id": 1,
    "name": "Pune",
    "code": "PUN",
    "region": 1,
    "region_name": "Pune",
    "state": 1,
    "state_name": "Maharashtra",
    "created_at": "2026-09-28T05:05:00.000000Z",
    "updated_at": "2026-09-28T05:05:00.000000Z"
}


18) api_name : district/update-district ( PATCH )
curl --location --request PATCH 'http://127.0.0.1:8000/api/update-district/?id=1' \
--header 'Authorization: Bearer <access_token>' \
--header 'Content-Type: application/json' \
--data '{
    "code": "PUN"
}'

response
{
    "id": 1,
    "name": "Pune",
    "code": "PUN",
    "region": 1,
    "region_name": "Pune",
    "state": 1,
    "state_name": "Maharashtra",
    "created_at": "2026-09-28T05:05:00.000000Z",
    "updated_at": "2026-09-28T05:06:00.000000Z"
}


19) api_name : district/delete-district ( DELETE )
curl --location --request DELETE 'http://127.0.0.1:8000/api/delete-district/?id=1' \
--header 'Authorization: Bearer <access_token>'

response
{}


20) api_name : area/add-area ( POST )
curl --location 'http://127.0.0.1:8000/api/add-area/' \
--header 'Authorization: Bearer <access_token>' \
--header 'Content-Type: application/json' \
--data '{
    "name": "Pune Area",
    "code": "PA",
    "district": 1
}'

response
{
    "id": 1,
    "name": "Pune Area",
    "code": "PA",
    "district": 1,
    "district_name": "Pune",
    "region": 1,
    "region_name": "Pune",
    "state": 1,
    "state_name": "Maharashtra",
    "created_at": "2026-09-28T05:07:00.000000Z",
    "updated_at": "2026-09-28T05:07:00.000000Z"
}


21) api_name : area/get-areas ( GET )
curl --location 'http://127.0.0.1:8000/api/get-areas/?district=1' \
--header 'Authorization: Bearer <access_token>'

response
[
    {
        "id": 1,
        "name": "Pune Area",
        "code": "PA",
        "district": 1,
        "district_name": "Pune",
        "region": 1,
        "region_name": "Pune",
        "state": 1,
        "state_name": "Maharashtra",
        "created_at": "2026-09-28T05:07:00.000000Z",
        "updated_at": "2026-09-28T05:07:00.000000Z"
    }
]


22) api_name : area/get-area-by-id ( GET )
curl --location 'http://127.0.0.1:8000/api/get-area-by-id/?id=1' \
--header 'Authorization: Bearer <access_token>'

response
{
    "id": 1,
    "name": "Pune Area",
    "code": "PA",
    "district": 1,
    "district_name": "Pune",
    "region": 1,
    "region_name": "Pune",
    "state": 1,
    "state_name": "Maharashtra",
    "created_at": "2026-09-28T05:07:00.000000Z",
    "updated_at": "2026-09-28T05:07:00.000000Z"
}


23) api_name : area/update-area ( PATCH )
curl --location --request PATCH 'http://127.0.0.1:8000/api/update-area/?id=1' \
--header 'Authorization: Bearer <access_token>' \
--header 'Content-Type: application/json' \
--data '{
    "code": "PA"
}'

response
{
    "id": 1,
    "name": "Pune Area",
    "code": "PA",
    "district": 1,
    "district_name": "Pune",
    "region": 1,
    "region_name": "Pune",
    "state": 1,
    "state_name": "Maharashtra",
    "created_at": "2026-09-28T05:07:00.000000Z",
    "updated_at": "2026-09-28T05:08:00.000000Z"
}


24) api_name : area/delete-area ( DELETE )
curl --location --request DELETE 'http://127.0.0.1:8000/api/delete-area/?id=1' \
--header 'Authorization: Bearer <access_token>'

response
{}


25) api_name : project/add-project ( POST )
curl --location 'http://127.0.0.1:8000/api/add-project/' \
--header 'Authorization: Bearer <access_token>' \
--header 'Content-Type: application/json' \
--data '{
    "name": "Pune Housing",
    "code": "PH",
    "area": 1
}'

response
{
    "id": 1,
    "name": "Pune Housing",
    "code": "PH",
    "area": 1,
    "area_name": "Pune Area",
    "district": 1,
    "district_name": "Pune",
    "region": 1,
    "region_name": "Pune",
    "state": 1,
    "state_name": "Maharashtra",
    "created_at": "2026-09-28T05:09:00.000000Z",
    "updated_at": "2026-09-28T05:09:00.000000Z"
}


26) api_name : project/get-projects ( GET )
curl --location 'http://127.0.0.1:8000/api/get-projects/?area=1' \
--header 'Authorization: Bearer <access_token>'

response
[
    {
        "id": 1,
        "name": "Pune Housing",
        "code": "PH",
        "area": 1,
        "area_name": "Pune Area",
        "district": 1,
        "district_name": "Pune",
        "region": 1,
        "region_name": "Pune",
        "state": 1,
        "state_name": "Maharashtra",
        "created_at": "2026-09-28T05:09:00.000000Z",
        "updated_at": "2026-09-28T05:09:00.000000Z"
    }
]


27) api_name : project/get-project-by-id ( GET )
curl --location 'http://127.0.0.1:8000/api/get-project-by-id/?id=1' \
--header 'Authorization: Bearer <access_token>'

response
{
    "id": 1,
    "name": "Pune Housing",
    "code": "PH",
    "area": 1,
    "area_name": "Pune Area",
    "district": 1,
    "district_name": "Pune",
    "region": 1,
    "region_name": "Pune",
    "state": 1,
    "state_name": "Maharashtra",
    "created_at": "2026-09-28T05:09:00.000000Z",
    "updated_at": "2026-09-28T05:09:00.000000Z"
}


28) api_name : project/update-project ( PATCH )
curl --location --request PATCH 'http://127.0.0.1:8000/api/update-project/?id=1' \
--header 'Authorization: Bearer <access_token>' \
--header 'Content-Type: application/json' \
--data '{
    "code": "PH"
}'

response
{
    "id": 1,
    "name": "Pune Housing",
    "code": "PH",
    "area": 1,
    "area_name": "Pune Area",
    "district": 1,
    "district_name": "Pune",
    "region": 1,
    "region_name": "Pune",
    "state": 1,
    "state_name": "Maharashtra",
    "created_at": "2026-09-28T05:09:00.000000Z",
    "updated_at": "2026-09-28T05:10:00.000000Z"
}


29) api_name : project/delete-project ( DELETE )
curl --location --request DELETE 'http://127.0.0.1:8000/api/delete-project/?id=1' \
--header 'Authorization: Bearer <access_token>'

response
{}


30) api_name : user/add-user ( POST )
curl --location 'http://127.0.0.1:8000/api/add-user/' \
--header 'Authorization: Bearer <access_token>' \
--header 'Content-Type: application/json' \
--data '{
    "username": "pune_area_head",
    "password": "AreaHead@123",
    "first_name": "Neha",
    "last_name": "Kulkarni",
    "email": "neha.area@example.com",
    "mobile_number": "9000000006",
    "designation": "AREA_HEAD",
    "state": "Maharashtra",
    "region": "Pune",
    "district": "Pune",
    "area": "Pune Area",
    "project": null
}'

response
{
    "id": 6,
    "username": "pune_area_head",
    "first_name": "Neha",
    "last_name": "Kulkarni",
    "email": "neha.area@example.com",
    "mobile_number": "9000000006",
    "designation": "AREA_HEAD",
    "designation_label": "Area Head",
    "state": 1,
    "state_name": "Maharashtra",
    "region": 1,
    "region_name": "Pune",
    "district": 1,
    "district_name": "Pune",
    "area": 1,
    "area_name": "Pune Area",
    "project": null,
    "project_name": null,
    "is_active": true,
    "created_at": "2026-09-28T05:10:00.000000Z",
    "updated_at": "2026-09-28T05:10:00.000000Z"
}


31) api_name : user/get-users ( GET )
curl --location 'http://127.0.0.1:8000/api/get-users/?designation=AREA_HEAD' \
--header 'Authorization: Bearer <access_token>'

response
[
    {
        "id": 6,
        "username": "pune_area_head",
        "first_name": "Neha",
        "last_name": "Kulkarni",
        "email": "neha.area@example.com",
        "mobile_number": "9000000006",
        "designation": "AREA_HEAD",
        "designation_label": "Area Head",
        "state": 1,
        "state_name": "Maharashtra",
        "region": 1,
        "region_name": "Pune",
        "district": 1,
        "district_name": "Pune",
        "area": 1,
        "area_name": "Pune Area",
        "project": null,
        "project_name": null,
        "is_active": true,
        "created_at": "2026-09-28T05:10:00.000000Z",
        "updated_at": "2026-09-28T05:10:00.000000Z"
    }
]


32) api_name : user/get-user-by-id ( GET )
curl --location 'http://127.0.0.1:8000/api/get-user-by-id/?id=6' \
--header 'Authorization: Bearer <access_token>'

response
{
    "id": 6,
    "username": "pune_area_head",
    "first_name": "Neha",
    "last_name": "Kulkarni",
    "email": "neha.area@example.com",
    "mobile_number": "9000000006",
    "designation": "AREA_HEAD",
    "designation_label": "Area Head",
    "state": 1,
    "state_name": "Maharashtra",
    "region": 1,
    "region_name": "Pune",
    "district": 1,
    "district_name": "Pune",
    "area": 1,
    "area_name": "Pune Area",
    "project": null,
    "project_name": null,
    "is_active": true,
    "created_at": "2026-09-28T05:10:00.000000Z",
    "updated_at": "2026-09-28T05:10:00.000000Z"
}


33) api_name : user/update-user ( PATCH )
curl --location --request PATCH 'http://127.0.0.1:8000/api/update-user/?id=6' \
--header 'Authorization: Bearer <access_token>' \
--header 'Content-Type: application/json' \
--data '{
    "mobile_number": "9000000016"
}'

response
{
    "id": 6,
    "username": "pune_area_head",
    "first_name": "Neha",
    "last_name": "Kulkarni",
    "email": "neha.area@example.com",
    "mobile_number": "9000000016",
    "designation": "AREA_HEAD",
    "designation_label": "Area Head",
    "state": 1,
    "state_name": "Maharashtra",
    "region": 1,
    "region_name": "Pune",
    "district": 1,
    "district_name": "Pune",
    "area": 1,
    "area_name": "Pune Area",
    "project": null,
    "project_name": null,
    "is_active": true,
    "created_at": "2026-09-28T05:10:00.000000Z",
    "updated_at": "2026-09-28T05:12:00.000000Z"
}


34) api_name : user/delete-user ( DELETE )
curl --location --request DELETE 'http://127.0.0.1:8000/api/delete-user/?id=2' \
--header 'Authorization: Bearer <access_token>'

response
{}


35) api_name : site/add-site ( POST )
curl --location 'http://127.0.0.1:8000/api/add-site/' \
--header 'Authorization: Bearer <access_token>' \
--header 'Content-Type: application/json' \
--data '{
    "name": "Shivaji Nagar Site",
    "code": "SN",
    "address": "Shivaji Nagar, Pune",
    "latitude": 18.530823,
    "longitude": 73.847466,
    "area": 1,
    "project": 1
}'

response
{
    "id": 1,
    "name": "Shivaji Nagar Site",
    "code": "SN",
    "address": "Shivaji Nagar, Pune",
    "latitude": "18.5308230",
    "longitude": "73.8474660",
    "area": 1,
    "area_name": "Pune Area",
    "project": 1,
    "project_name": "Pune Housing",
    "district": 1,
    "district_name": "Pune",
    "region": 1,
    "region_name": "Pune",
    "state": 1,
    "state_name": "Maharashtra",
    "is_active": true,
    "created_by": 6,
    "created_by_username": "pune_area_head",
    "created_at": "2026-09-28T05:20:00.000000Z",
    "updated_at": "2026-09-28T05:20:00.000000Z"
}


36) api_name : site/get-sites ( GET )
curl --location 'http://127.0.0.1:8000/api/get-sites/?area=1' \
--header 'Authorization: Bearer <access_token>'

response
[
    {
        "id": 1,
        "name": "Shivaji Nagar Site",
        "code": "SN",
        "address": "Shivaji Nagar, Pune",
        "latitude": "18.5308230",
        "longitude": "73.8474660",
        "area": 1,
        "area_name": "Pune Area",
        "project": 1,
        "project_name": "Pune Housing",
        "district": 1,
        "district_name": "Pune",
        "region": 1,
        "region_name": "Pune",
        "state": 1,
        "state_name": "Maharashtra",
        "is_active": true,
        "created_by": 6,
        "created_by_username": "pune_area_head",
        "created_at": "2026-09-28T05:20:00.000000Z",
        "updated_at": "2026-09-28T05:20:00.000000Z"
    }
]


37) api_name : site/get-site-by-id ( GET )
curl --location 'http://127.0.0.1:8000/api/get-site-by-id/?id=1' \
--header 'Authorization: Bearer <access_token>'

response
{
    "id": 1,
    "name": "Shivaji Nagar Site",
    "code": "SN",
    "address": "Shivaji Nagar, Pune",
    "latitude": "18.5308230",
    "longitude": "73.8474660",
    "area": 1,
    "area_name": "Pune Area",
    "project": 1,
    "project_name": "Pune Housing",
    "district": 1,
    "district_name": "Pune",
    "region": 1,
    "region_name": "Pune",
    "state": 1,
    "state_name": "Maharashtra",
    "is_active": true,
    "created_by": 6,
    "created_by_username": "pune_area_head",
    "created_at": "2026-09-28T05:20:00.000000Z",
    "updated_at": "2026-09-28T05:20:00.000000Z"
}


38) api_name : site/update-site ( PATCH )
curl --location --request PATCH 'http://127.0.0.1:8000/api/update-site/?id=1' \
--header 'Authorization: Bearer <access_token>' \
--header 'Content-Type: application/json' \
--data '{
    "address": "Shivaji Nagar, Pune 411005",
    "latitude": 18.530823,
    "longitude": 73.847466
}'

response
{
    "id": 1,
    "name": "Shivaji Nagar Site",
    "code": "SN",
    "address": "Shivaji Nagar, Pune 411005",
    "latitude": "18.5308230",
    "longitude": "73.8474660",
    "area": 1,
    "area_name": "Pune Area",
    "project": 1,
    "project_name": "Pune Housing",
    "district": 1,
    "district_name": "Pune",
    "region": 1,
    "region_name": "Pune",
    "state": 1,
    "state_name": "Maharashtra",
    "is_active": true,
    "created_by": 6,
    "created_by_username": "pune_area_head",
    "created_at": "2026-09-28T05:20:00.000000Z",
    "updated_at": "2026-09-28T05:22:00.000000Z"
}


39) api_name : site/delete-site ( DELETE )
curl --location --request DELETE 'http://127.0.0.1:8000/api/delete-site/?id=1' \
--header 'Authorization: Bearer <access_token>'

response
{}
