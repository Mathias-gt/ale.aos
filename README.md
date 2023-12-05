

# Alcatel-Lucent Enterprise AOS Collection
[![CI](https://zuul-ci.org/gated.svg)](https://dashboard.zuul.ansible.com/t/ansible/project/github.com/ansible-collections/ale.aos) <!--[![Codecov](https://img.shields.io/codecov/c/github/ansible-collections/ale.aos)](https://codecov.io/gh/ansible-collections/ale.aos)-->
[![Codecov](https://codecov.io/gh/ansible-collections/ale.aos/branch/main/graph/badge.svg)](https://codecov.io/gh/ansible-collections/ale.aos)
[![CI](https://github.com/ansible-collections/ale.aos/actions/workflows/tests.yml/badge.svg?branch=main&event=schedule)](https://github.com/ansible-collections/ale.aos/actions/workflows/tests.yml)

The Ansible Alcatel-Lucent Enterprise AOS collection includes a variety of Ansible content to help automate the management of Alcatel-Lucent Enterprise AOS network appliances.

This collection has been tested against Alcatel-Lucent Enterprise AOS TDB.

<!--start requires_ansible-->
## Ansible version compatibility

This collection has been tested against following Ansible versions: **>=2.14.0**.

For collections that support Ansible 2.9, please ensure you update your `network_os` to use the
fully qualified collection name (for example, `ale.aos.aos`).
Plugins and modules within a collection may be tested with only specific Ansible versions.
A collection may contain metadata that identifies these versions.
PEP440 is the schema used to describe the versions of Ansible.
<!--end requires_ansible-->

### Supported connections
The Alcatel-Lucent Enterprise AOS collection supports ``network_cli`` connection.

## Included content

<!--start collection content-->
### Cliconf plugins
Name | Description
--- | ---
[alcatel.aos.aos](https://github.com/Mathias-gt/ale.aos/blob/main/docs/ale.aos.aos_cliconf.rst)|Use aos cliconf to run command on Alcatel-Lucent Enterprise AOS platform

### Modules
Name | Description
--- | ---
[alcatel.aos.aos_config](https://github.com/Mathias-gt/ale.aos/blob/main/docs/ale.aos.aos_config_module.rst)|Manage Alcatel-Lucent Enterprise AOS configuration sections

<!--end collection content-->

Click the ``Content`` button to see the list of content included in this collection.

## Installing this collection

You can install the Alcatel-Lucent Enterprise AOS collection with the Ansible Galaxy CLI:

    ansible-galaxy collection install ale.aos

You can also include it in a `requirements.yml` file and install it with `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: ale.aos
```
## Using this collection


This collection includes [network resource modules](https://docs.ansible.com/ansible/latest/network/user_guide/network_resource_modules.html).

### Using modules from the Alcatel-Lucent Enterprise AOS collection in your playbooks

You can call modules by their Fully Qualified Collection Namespace (FQCN), such as `alcatel.aos.aos_config`.
The following example task replaces configuration changes in the existing configuration on a Alcatel-Lucent Enterprise AOS network device, using the FQCN:

```yaml
---
  - name: Replace device configuration of specified L2 interfaces with provided configuration.
    alcatel.aos.aos_config:
      lines:
        - interfaces port 1/1/1 admin-state disable
```

### See Also:

* [Alcatel-Lucent Enterprise AOS Platform Options](https://docs.ansible.com/ansible/latest/network/user_guide/platform_aos.html)
* [Ansible Using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more details.

## Contributing to this collection

We welcome community contributions to this collection. If you find problems, please open an issue or create a PR against the [Alcatel-Lucent Enterprise AOS collection repository](https://github.com/ansible-collections/ale.aos). See [Contributing to Ansible-maintained collections](https://docs.ansible.com/ansible/devel/community/contributing_maintained_collections.html#contributing-maintained-collections) for complete details.

You can also join us on:

- IRC - the ``#ansible-network`` [irc.libera.chat](https://libera.chat/) channel
- Slack - https://ansiblenetwork.slack.com

See the [Ansible Community Guide](https://docs.ansible.com/ansible/latest/community/index.html) for details on contributing to Ansible.

### Code of Conduct
This collection follows the Ansible project's
[Code of Conduct](https://docs.ansible.com/ansible/devel/community/code_of_conduct.html).
Please read and familiarize yourself with this document.

## Changelogs
<!--Add a link to a changelog.md file or an external docsite to cover this information. -->
## Release notes

Release notes are available [here](https://github.com/ansible-collections/ale.aos/blob/main/CHANGELOG.rst).

## Roadmap

<!-- Optional. Include the roadmap for this collection, and the proposed release/versioning strategy so users can anticipate the upgrade/update cycle. -->

## More information

- [Ansible network resources](https://docs.ansible.com/ansible/latest/network/getting_started/network_resources.html)
- [Ansible Collection overview](https://github.com/ansible-collections/overview)
- [Ansible User guide](https://docs.ansible.com/ansible/latest/user_guide/index.html)
- [Ansible Developer guide](https://docs.ansible.com/ansible/latest/dev_guide/index.html)
- [Ansible Community code of conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html)

## Licensing

GNU General Public License v3.0 or later.

See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.
