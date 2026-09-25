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
| Create user | `POST /api/users/` |
| List users | `GET /api/users/` |
| User details | `GET /api/users/<id>/` |
| Update user | `PUT /api/users/<id>/` or `PATCH /api/users/<id>/` |
| Delete user | `DELETE /api/users/<id>/` |

List filters, all optional:

- `?search=ravi` searches name, username, email and mobile number
- `?designation=REGION_HEAD`
- `?state=1&region=2&district=3&area=4&project=5`

Designation values:

`CMD`, `MAIN_ADMIN`, `STATE_HEAD`, `REGION_HEAD`, `DISTRICT_HEAD`, `AREA_HEAD`, `PROJECT_HEAD`

Location rules for a new user:

| Designation | Must send | Must leave empty |
| --- | --- | --- |
| CMD | nothing | state, region, district, area, project |
| Main Admin | nothing | state, region, district, area, project |
| State Head | state | region, district, area, project |
| Region Head | state and region | district, area, project |
| District Head | state, region and district | area, project |
| Area Head | state, region, district and area | project |
| Project Head | state, region, district, area and project | nothing extra |

The region must belong to the state. The district must belong to the region. The area must belong to the district. The project must belong to the area.

Password is required when creating a user. It is optional when updating. It must be at least 8 characters, not only numbers, and not a very common password.

Mobile number is 10 to 15 digits. A leading `+` is allowed. Email, username and mobile number must be unique.

## State, Region, District, Area and Project

Each one has the same five actions. All of them need a Bearer token.

| Record | List / Create | One record |
| --- | --- | --- |
| State | `/api/states/` | `/api/states/<id>/` |
| Region | `/api/regions/` | `/api/regions/<id>/` |
| District | `/api/districts/` | `/api/districts/<id>/` |
| Area | `/api/areas/` | `/api/areas/<id>/` |
| Project | `/api/projects/` | `/api/projects/<id>/` |

Use `POST` to create, `GET` to read, `PUT` or `PATCH` to update, and `DELETE` to delete.

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
| Create site | `POST /api/sites/` |
| List sites | `GET /api/sites/` |
| Site details | `GET /api/sites/<id>/` |
| Update site | `PUT /api/sites/<id>/` or `PATCH /api/sites/<id>/` |
| Delete site | `DELETE /api/sites/<id>/` |

A site must belong to an **area** and a **project**, and that project must belong to that area.

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

Send username and password. The response has:

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

## API endpoint list

| Method | Address | Who can call it |
| --- | --- | --- |
| POST | `/api/auth/login/` | Anyone |
| POST | `/api/auth/refresh/` | Anyone with a refresh token |
| POST | `/api/auth/logout/` | Logged-in user |
| GET, POST | `/api/users/` | Logged-in user, inside their branch |
| GET, PUT, PATCH, DELETE | `/api/users/<id>/` | Logged-in user, inside their branch |
| GET, POST | `/api/states/` | Logged-in user, inside their branch |
| GET, PUT, PATCH, DELETE | `/api/states/<id>/` | Logged-in user, inside their branch |
| GET, POST | `/api/regions/` | Logged-in user, inside their branch |
| GET, PUT, PATCH, DELETE | `/api/regions/<id>/` | Logged-in user, inside their branch |
| GET, POST | `/api/districts/` | Logged-in user, inside their branch |
| GET, PUT, PATCH, DELETE | `/api/districts/<id>/` | Logged-in user, inside their branch |
| GET, POST | `/api/areas/` | Logged-in user, inside their branch |
| GET, PUT, PATCH, DELETE | `/api/areas/<id>/` | Logged-in user, inside their branch |
| GET, POST | `/api/projects/` | Logged-in user, inside their branch |
| GET, PUT, PATCH, DELETE | `/api/projects/<id>/` | Logged-in user, inside their branch |
| GET, POST | `/api/sites/` | Logged-in user. POST is Area Head only |
| GET, PUT, PATCH, DELETE | `/api/sites/<id>/` | Logged-in user, inside their branch |

## Example login request

```text
POST http://127.0.0.1:8000/api/auth/login/
Content-Type: application/json

{
  "username": "cmd",
  "password": "CmdAdmin@123"
}
```

Example response:

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "cmd",
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
GET http://127.0.0.1:8000/api/states/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Create a region:

```text
POST http://127.0.0.1:8000/api/regions/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "name": "Pune",
  "code": "PN",
  "state": 1
}
```

Create the Area Head of Pune Area:

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

Create a site (only when logged in as that Area Head):

```json
{
  "name": "Shivaji Nagar Site",
  "code": "SN",
  "address": "Shivaji Nagar, Pune",
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
python manage.py createsuperuser
python manage.py runserver
```

`createsuperuser` asks for username, email, mobile number, first name, last name and password. That account is the **CMD**.

Then open `http://127.0.0.1:8000/api/auth/login/`.

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
