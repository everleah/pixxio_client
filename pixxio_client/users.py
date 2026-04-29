from ._base import ResourceBase


class User(ResourceBase):
    """
    Resource for managing user accounts in PIXXIO.

    Users represent individual login accounts inside the PIXXIO system. User
    records contain profile information (name, e-mail, language, …) and link
    to permission groups that control what each user may do.

    API endpoint: ``/api/v1/users``

    Available operations (inherited):
        - ``get()``              – list all users
        - ``get(id)``            – retrieve a specific user by ID
        - ``post(json_data)``    – create a new user account
        - ``put(id, json_data)`` – update an existing user (e.g. change name or group)
        - ``delete(id=id)``      – delete a user account

    Example::

        from pixxio_client import Client
        from pixxio_client.users import User

        client = Client.create_client("api-key", "company.pixxio.com")
        users = User(client)

        # List all users
        all_users = users.get()

        # Retrieve a single user
        me = users.get(42)
        print(me.firstName, me.lastName, me.email)

        # Update a user’s display name
        users.put(42, json_data={"firstName": "Jane"})
    Response field filtering::

        users.set_response_fields(["id", "displayName", "email", "isActive"])
        result = users.get()  # only returns the specified fields    """

    NAME = "users"
    