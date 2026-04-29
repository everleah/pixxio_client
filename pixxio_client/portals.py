
from ._base import ReadOnlyResourceBase


class Portal(ReadOnlyResourceBase):
    """
    Resource for accessing PIXXIO portals.

    Portals are publicly accessible entry points inside PIXXIO that can expose
    curated collections of assets to external users. This base class provides
    read access to the portal list and individual portal details.

    API endpoint: ``/api/v1/portals``

    Available operations (inherited):
        - ``get()``  – list all portals
        - ``get(id)`` – retrieve a specific portal by ID

    Example::

        from pixxio_client import Client
        from pixxio_client.portals import Portal

        client = Client.create_client("api-key", "company.pixxio.com")
        portals = Portal(client)

        all_portals = portals.get()
        my_portal  = portals.get(42)

    Response field filtering::

        portals.set_response_fields(["id", "name"])
        result = portals.get()  # only returns the specified fields

    Note:
        Response field filtering is suppressed automatically in
        :class:`PortalPage` and :class:`PortalUser`, as those
        sub-endpoints do not support the parameter.
    """

    NAME = "portals"


class PortalPage(Portal):
    """
    Resource for reading pages within a PIXXIO portal.

    Each portal can contain multiple pages that group and display assets.
    This class retrieves the page structure of a given portal.

    API endpoint: ``/api/v1/portals/{id}/pages``

    Note:
        The ``responseFields`` parameter is not supported by this endpoint and
        is automatically suppressed by the client.

    Example::

        from pixxio_client.portals import PortalPage

        pages = PortalPage(client)
        result = pages.get(42)   # returns pages of portal 42
    """

    def get(self, id, **params):
        """
        Retrieve the pages of a portal.

        Args:
            id: ID of the portal whose pages should be retrieved.
            **params: Additional query parameters forwarded to the API.

        Returns:
            ResponseData: Object containing the portal's pages.

        Example::

            pages = PortalPage(client)
            result = pages.get(42)
        """
        with self._without_response_fields():
            return self._get(
                endpoint_base=f"{self.endpoint_base}/{id}/pages",
                **params)


class PortalUser(Portal):
    """
    Resource for reading users associated with a PIXXIO portal.

    Portal users are external or internal accounts that have access to a specific
    portal. This class supports retrieving the currently authenticated portal
    user as well as any specific user by ID.

    API endpoints:
        - ``GET /api/v1/portals/{id}/users/current`` – current portal user
        - ``GET /api/v1/portals/{id}/users/{user_id}`` – specific portal user

    Note:
        The ``responseFields`` parameter is not supported by this endpoint and
        is automatically suppressed by the client.

    Example::

        from pixxio_client.portals import PortalUser

        pu = PortalUser(client)

        # Current authenticated portal user
        current = pu.get(42)

        # Specific user within the portal
        specific = pu.get(42, user_id=7)
    """

    def get(self, id, user_id=None, **params):
        """
        Retrieve a portal user.

        Args:
            id: ID of the portal.
            user_id: Optional user ID within the portal.  When omitted, the
                currently authenticated portal user is returned.
            **params: Additional query parameters forwarded to the API.

        Returns:
            ResponseData: Object containing the portal user's data.

        Example::

            pu = PortalUser(client)
            current  = pu.get(42)
            specific = pu.get(42, user_id=7)
        """
        with self._without_response_fields():
            if user_id is None:
                return self._get(
                    endpoint_base=f"{self.endpoint_base}/{id}/users/current",
                    **params)
            return self._get(
                endpoint_base=f"{self.endpoint_base}/{id}/users/{user_id}",
                **params)
        