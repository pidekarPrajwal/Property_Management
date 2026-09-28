# Property Management

This project keeps track of the organisation and the people who work in it.

The organisation is a tree:

```text
State
  └── Region
       └── District
            └── Area
                 └── Project
                      └── Site
```

People sit on that tree. A person can only see and change the part of the tree that belongs to them.

## What was changed

The project already had a Django project named `configuration` and an empty app named `setup`.

These pieces were added:

- A new app named `user` for login and people.
- Organisation records in the existing `setup` app: State, Region, District, Area, Project and Site.
- Login with a Bearer token.
- Rules so a person cannot open data outside their place in the organisation.

Each module follows the same order: model, then serializers, then views, then URLs. Serializers and views are split by record. Login stays separate from the user add/list/update/delete calls. Models were not changed.

The old admin page at `/admin/` is still there. The database was not changed by this work. You still need to create the tables yourself. The commands are at the end of this file.

## User hierarchy

```text
CMD
 └── Main Admin
      └── State Head
           └── Region Head
                └── District Head
                     └── Area Head
                          └── Project Head
```

A simple example:

```text
CMD
 └── Main Admin
      └── State Head of Maharashtra
           └── Region Head of Pune
                └── District Head of Pune
                     └── Area Head of Pune Area
                          └── Project Head of one project in that area
```

## What each designation can do

Every designation value used by the API is shown in brackets.

**CMD (`CMD`)**  
The top person. Can see every state, region, district, area, project, site and user. Can create and change all of them, except a site. A site can only be created by an Area Head.

**Main Admin (`MAIN_ADMIN`)**  
Same view of all data as CMD. Can create and change people who are below Main Admin. Cannot create another CMD or another Main Admin. Cannot create a site.

**State Head (`STATE_HEAD`)**  
Linked to one state, for example Maharashtra. Can see that state and everything under it: its regions, districts, areas, projects, sites and the people in that state. Cannot see Gujarat, or anyone who works only in Gujarat. Can create people below State Head, but only inside Maharashtra. Cannot create a site.

**Region Head (`REGION_HEAD`)**  
Linked to one state and one region, for example Pune inside Maharashtra. Can see the Pune region and everything under it. Can see their own state name, but cannot see other regions in Maharashtra, and cannot change the state. Cannot create a site.

**District Head (`DISTRICT_HEAD`)**  
Linked to one district. Can see that district and everything under it. Can see the state and region above that district. Cannot see a neighbouring district.

**Area Head (`AREA_HEAD`)**  
Linked to one area. Can see that area, its projects and its sites. This is the only designation that can create a site, and only inside their own area.

**Project Head (`PROJECT_HEAD`)**  
Linked to one project. Can see that project and its sites. Cannot see a neighbouring project, even in the same area. Cannot create users, projects or sites.

## How the hierarchy controls what you see

The API checks the logged-in person on every request. Changing an id in the request does not open another branch.

- **CMD and Main Admin** see the whole organisation.
- **Everyone else** sees:
  - their own place
  - the single path above them (so a Pune Region Head can see Maharashtra, but not Gujarat)
  - everything below them
- They **cannot** see a neighbouring branch. A Pune Region Head cannot see Nashik.
- They **can change** their own place and everything below it.
- They **cannot change** the levels above them. A Region Head can see the state, but cannot rename it or add another region.
- A person can **create or edit users only below their own designation**, and only inside their own branch.
- A person **cannot** change their own designation or their own place. They can change their name, email, mobile number and password.
- A person **cannot** delete their own account.

If you ask for a record outside your branch, the API responds as if it is not there (`404`). If you try to create or move a record into a place you do not manage, the API refuses (`403`). If a region does not belong to the state you selected, the API says the relationship is invalid (`400`).

## User CRUD

These calls all need a Bearer token.

| Action | Method and address |
| --- | --- |
| Create user | `POST /api/add-user/` |
| List users | `GET /api/get-users/` |
| User details | `GET /api/get-user-by-id/?id=1` |
| Update user | `PUT` or `PATCH /api/update-user/?id=1` |
| Delete user | `DELETE /api/delete-user/?id=1` |

Detail, update and delete do not put the id in the path. Send `?id=` (or `id` in the body for update and delete).

List filters, all optional:

- `?search=ravi` searches name, username, email and mobile number
- `?designation=REGION_HEAD`
- `?state=1&region=2&district=3&area=4&project=5`

Designation values:

`CMD`, `MAIN_ADMIN`, `STATE_HEAD`, `REGION_HEAD`, `DISTRICT_HEAD`, `AREA_HEAD`, `PROJECT_HEAD`

Location rules for a new user:

| Designation | Must send | Optional |
| --- | --- | --- |
| CMD | nothing | nothing; leave every place empty |
| Main Admin | nothing | nothing; leave every place empty |
| State Head | state, for example Maharashtra | region, district, area, project |
| Region Head | state and region | district, area, project |
| District Head | state, region and district | area, project |
| Area Head | state, region, district and area | project |
| Project Head | state, region, district, area and project | nothing extra |

Send each place as its name or its id. If that name does not exist yet, CMD or Main Admin creates it while adding the user. A State Head sends `"state": "Gujrat"` and leaves region, district, area, and project empty. A Region Head also sends the region name, and the same pattern continues down to Project Head. `0` is empty. The region must belong to the state. The district must belong to the region. The area must belong to the district. The project must belong to the area.

Password is required when creating a user. It is optional when updating. It must be at least 8 characters, not only numbers, and not a very common password.

Mobile number is 10 to 15 digits. A leading `+` is allowed. Email, username and mobile number must be unique.

## State, Region, District, Area and Project

Each one has the same five actions. All of them need a Bearer token.

| Record | Create | List | One record | Update | Delete |
| --- | --- | --- | --- | --- | --- |
| State | `POST /api/add-state/` | `GET /api/get-states/` | `GET /api/get-state-by-id/?id=1` | `PUT` or `PATCH /api/update-state/?id=1` | `DELETE /api/delete-state/?id=1` |
| Region | `POST /api/add-region/` | `GET /api/get-regions/` | `GET /api/get-region-by-id/?id=1` | `PUT` or `PATCH /api/update-region/?id=1` | `DELETE /api/delete-region/?id=1` |
| District | `POST /api/add-district/` | `GET /api/get-districts/` | `GET /api/get-district-by-id/?id=1` | `PUT` or `PATCH /api/update-district/?id=1` | `DELETE /api/delete-district/?id=1` |
| Area | `POST /api/add-area/` | `GET /api/get-areas/` | `GET /api/get-area-by-id/?id=1` | `PUT` or `PATCH /api/update-area/?id=1` | `DELETE /api/delete-area/?id=1` |
| Project | `POST /api/add-project/` | `GET /api/get-projects/` | `GET /api/get-project-by-id/?id=1` | `PUT` or `PATCH /api/update-project/?id=1` | `DELETE /api/delete-project/?id=1` |

Relationships:

- A region must send `state`.
- A district must send `region`.
- An area must send `district`.
- A project must send `area`.

Who can create them:

- Only CMD and Main Admin can create a state.
- A State Head can add regions, districts, areas and projects inside their state.
- A Region Head can add districts, areas and projects inside their region. They cannot add a region.
- A District Head can add areas and projects inside their district.
- An Area Head can add projects inside their area.
- A Project Head cannot add another project. They can update their own project name.

You cannot delete a parent while something still hangs from it. For example, you cannot delete Maharashtra while it still has a region. The API explains that instead of deleting the children.

Optional filters:

- `?search=pune` matches the name
- Regions: `?state=1`
- Districts: `?state=1&region=2`
- Areas: `?state=1&region=2&district=3`
- Projects: `?state=1&region=2&district=3&area=4`

## Site CRUD

| Action | Method and address |
| --- | --- |
| Create site | `POST /api/add-site/` |
| List sites | `GET /api/get-sites/` |
| Site details | `GET /api/get-site-by-id/?id=1` |
| Update site | `PUT` or `PATCH /api/update-site/?id=1` |
| Delete site | `DELETE /api/delete-site/?id=1` |

A site must belong to an **area** and a **project**, and that project must belong to that area.

`latitude` and `longitude` are two separate fields. Send them as numbers on create or update. They are stored on the site and returned in the site list and the dashboard. Either field can be left out. Latitude must be between -90 and 90. Longitude must be between -180 and 180.

Optional filters: `?search=`, `?state=`, `?region=`, `?district=`, `?area=`, `?project=`.

People can view, update and delete sites inside their own branch. A Project Head only sees sites of their own project.

## Site creation rule

**Only an Area Head can create a site.**

CMD, Main Admin, State Head, Region Head, District Head and Project Head all receive `403` if they try to create a site.

The Area Head can only create a site inside **their own area**, and the project must belong to that area. Sending another area id does not work.

## JWT login and logout

Login is the only public call. Everything else needs:

```text
Authorization: Bearer <access_token>
```

### Login

`POST /api/auth/login/`

A fixed account is created for you when the server starts. You do not need `createsuperuser`.

```json
{
  "username": "admin",
  "password": "123456"
}
```

That account is the CMD. The response has:

- `access` — use this as the Bearer token. It lasts 60 minutes.
- `refresh` — use this to get a new access token, or to log out. It lasts 7 days.
- `user` — the person's details.

### Refresh

`POST /api/auth/refresh/`

```json
{ "refresh": "<refresh_token>" }
```

This call is public because the refresh token itself proves who is asking.

### Logout

`POST /api/auth/logout/`

Send the Bearer access token, and the refresh token in the body:

```json
{ "refresh": "<refresh_token>" }
```

Logout puts that refresh token on a block list. It cannot be used again. The access token cannot be deleted, because that is how this kind of token works. It stops working after 60 minutes. After logout, do not use the access token again.

## API documentation (Swagger)

The same APIs are listed in Swagger. The API addresses do not change.

| Page | Address |
| --- | --- |
| Swagger UI | `http://127.0.0.1:8000/swagger/` |
| ReDoc | `http://127.0.0.1:8000/redoc/` |
| OpenAPI schema | `http://127.0.0.1:8000/schema/` |

How to try a protected API in Swagger:

1. Call **Login** under Authentication. Copy the `access` value.
2. Click **Authorize**.
3. Enter `Bearer <access_token>`, using that access value. Example: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
4. Click Authorize, then close the box.
5. Try a protected call, such as Get states.

Login and refresh stay open without that header. Every other API shows a lock. There is no Attendance API in this project, so Swagger does not have an Attendance group.

## Dashboard

`GET /api/dashboard/`

Send `Authorization: Bearer <access_token>`. With no filter, the response is every person and place that head is allowed to see.

Optional filter: `?designation=STATE_HEAD`. That returns the state heads and the regions, districts, areas, projects, sites, and people under their states. `REGION_HEAD`, `DISTRICT_HEAD`, `AREA_HEAD`, and `PROJECT_HEAD` do the same for their own level. `CMD` and `MAIN_ADMIN` return those people and every place still visible to the caller.

- CMD and Main Admin see every state, region, district, area, project, site, and user.
- A State Head sees their state and everything under it, and not another state.
- A Region Head sees their region and everything under it.
- A District Head sees their district and everything under it.
- An Area Head sees their area, its projects, and its sites.
- A Project Head sees their project and its sites.

The reply has `user` (the logged-in person), `counts`, and the matching lists.

## API endpoint list

| Method | Address | Who can call it |
| --- | --- | --- |
| GET | `/api/dashboard/` | Logged-in head, only their own branch |
| POST | `/api/auth/login/` | Anyone |
| POST | `/api/auth/refresh/` | Anyone with a refresh token |
| POST | `/api/auth/logout/` | Logged-in user |
| POST | `/api/add-user/` | Logged-in user, inside their branch |
| GET | `/api/get-users/` | Logged-in user, inside their branch |
| GET | `/api/get-user-by-id/?id=` | Logged-in user, inside their branch |
| PUT, PATCH | `/api/update-user/?id=` | Logged-in user, inside their branch |
| DELETE | `/api/delete-user/?id=` | Logged-in user, inside their branch |
| POST | `/api/add-state/` | CMD and Main Admin |
| GET | `/api/get-states/` | Logged-in user, inside their branch |
| GET | `/api/get-state-by-id/?id=` | Logged-in user, inside their branch |
| PUT, PATCH | `/api/update-state/?id=` | Logged-in user, inside their branch |
| DELETE | `/api/delete-state/?id=` | Logged-in user, inside their branch |
| POST | `/api/add-region/` | Logged-in user, inside their branch |
| GET | `/api/get-regions/` | Logged-in user, inside their branch |
| GET | `/api/get-region-by-id/?id=` | Logged-in user, inside their branch |
| PUT, PATCH | `/api/update-region/?id=` | Logged-in user, inside their branch |
| DELETE | `/api/delete-region/?id=` | Logged-in user, inside their branch |
| POST | `/api/add-district/` | Logged-in user, inside their branch |
| GET | `/api/get-districts/` | Logged-in user, inside their branch |
| GET | `/api/get-district-by-id/?id=` | Logged-in user, inside their branch |
| PUT, PATCH | `/api/update-district/?id=` | Logged-in user, inside their branch |
| DELETE | `/api/delete-district/?id=` | Logged-in user, inside their branch |
| POST | `/api/add-area/` | Logged-in user, inside their branch |
| GET | `/api/get-areas/` | Logged-in user, inside their branch |
| GET | `/api/get-area-by-id/?id=` | Logged-in user, inside their branch |
| PUT, PATCH | `/api/update-area/?id=` | Logged-in user, inside their branch |
| DELETE | `/api/delete-area/?id=` | Logged-in user, inside their branch |
| POST | `/api/add-project/` | Logged-in user, inside their branch |
| GET | `/api/get-projects/` | Logged-in user, inside their branch |
| GET | `/api/get-project-by-id/?id=` | Logged-in user, inside their branch |
| PUT, PATCH | `/api/update-project/?id=` | Logged-in user, inside their branch |
| DELETE | `/api/delete-project/?id=` | Logged-in user, inside their branch |
| POST | `/api/add-site/` | Area Head only, inside their area |
| GET | `/api/get-sites/` | Logged-in user, inside their branch |
| GET | `/api/get-site-by-id/?id=` | Logged-in user, inside their branch |
| PUT, PATCH | `/api/update-site/?id=` | Logged-in user, inside their branch |
| DELETE | `/api/delete-site/?id=` | Logged-in user, inside their branch |

## Example login request

```text
POST http://127.0.0.1:8000/api/auth/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "123456"
}
```

Example response:

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "first_name": "Asha",
    "last_name": "Patil",
    "email": "asha@example.com",
    "mobile_number": "9000000001",
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
    "created_at": "2026-09-25T10:00:00Z",
    "updated_at": "2026-09-25T10:00:00Z"
  }
}
```

## Example Bearer token request

```text
GET http://127.0.0.1:8000/api/get-states/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Create a region:

```text
POST http://127.0.0.1:8000/api/add-region/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "name": "Pune",
  "code": "PN",
  "state": 1
}
```

Create a user with `POST /api/add-user/`. Example, the Area Head of Pune Area:

```json
{
  "username": "pune_area_head",
  "password": "AreaHead@123",
  "first_name": "Neha",
  "last_name": "Kulkarni",
  "email": "neha@example.com",
  "mobile_number": "9000000006",
  "designation": "AREA_HEAD",
  "state": 1,
  "region": 1,
  "district": 1,
  "area": 1
}
```

Create a site with `POST /api/add-site/` (only when logged in as that Area Head):

```json
{
  "name": "Shivaji Nagar Site",
  "code": "SN",
  "address": "Shivaji Nagar, Pune",
  "latitude": 18.530823,
  "longitude": 73.847466,
  "area": 1,
  "project": 1
}
```

## Example responses you will see

Missing or bad token (`401`):

```json
{ "detail": "Authentication credentials were not provided." }
```

Wrong branch (`403`):

```json
{ "detail": "Only an Area Head can create a site." }
```

Invalid link (`400`):

```json
{ "region": ["The selected region does not belong to the selected state."] }
```

Record outside your branch (`404`):

```json
{ "detail": "Not found." }
```

Delete blocked because children exist (`400`):

```json
{
  "detail": "This record cannot be deleted because other records still use it. Remove or move those records first."
}
```

## Project setup

From the project folder, with the virtual environment turned on:

```text
venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations user setup
python manage.py migrate
python manage.py runserver
```

You do not need `createsuperuser`. After migrate, starting the server creates this login:

```text
username: admin
password: 123456
```

Then open `http://127.0.0.1:8000/api/auth/login/`.

API documentation is at `http://127.0.0.1:8000/swagger/`.

The admin site is still at `http://127.0.0.1:8000/admin/`.

## How to test the APIs

A ready-made script calls every API with `curl.exe`. It creates the Maharashtra example, then checks the rules (a State Head cannot create a site, a Project Head cannot see another project, and so on).

1. Run the setup commands above and create the CMD user.
2. Open `api_curl.ps1` and set `$CmdUsername` and `$CmdPassword` to that CMD account.
3. In PowerShell, from the project folder:

```text
powershell -ExecutionPolicy Bypass -File .\api_curl.ps1
```

The script leaves the Maharashtra sample data in the database so you can keep testing. It tries to delete the extra Gujarat state at the end.

## Important rules

1. Every API except login and refresh needs `Authorization: Bearer <access_token>`.
2. Only an Area Head can create a site, and only in their own area.
3. A region must belong to the selected state. The same idea applies down the tree.
4. Sending another id does not let you jump into someone else's branch.
5. You can manage users only if they are below your designation.
6. You cannot change your own designation or location, and you cannot delete yourself.
7. You cannot delete a state, region, district, area or project while lower records still use it.
8. Logout blocks the refresh token. The access token expires after 60 minutes.
9. Database commands were not run for you. Run `makemigrations` and `migrate` before the first start.
