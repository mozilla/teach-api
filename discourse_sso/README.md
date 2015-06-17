The `discourse_sso` Dajngo app provides a [Discourse SSO][sso] endpoint 
for the Django site, allowing users to login to Discourse with their
Webmaker credentials and use the same username that they have
on Webmaker.

To enable Discourse SSO, ensure the following Django settings
are configured:

* `DISCOURSE_SSO_SECRET` is the secret shared between your Django
  site and the Discourse site.
* `DISCOURSE_SSO_ORIGIN` is the origin of your Discourse site, e.g.
  `http://my-discourse.org`.

On the Discourse side, you'll want to make sure the following are
configured under "Settings > Login" in Discourse's admin panel:

* "sso secret" should be identical to `DISCOURSE_SSO_SECRET`.
* "enable sso" should be checked.
* "sso url" should be set to the origin of your site, followed
  by `/discourse_sso/`. For example, `http://example.org/discourse_sso/`.
* You'll also probably want to check some of the checkboxes for SSO
  overrides, so that user information on your Discourse always
  reflects the state of the user's Webmaker account as closely as
  possible.

<!-- Links -->

  [sso]: https://meta.discourse.org/t/official-single-sign-on-for-discourse/13045
