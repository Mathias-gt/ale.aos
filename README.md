

# Alcatel-Lucent Enterprise AOS Collectiontest

The Ansible Alcatel-Lucent Enterprise AOS collection includes a variety of Ansible content to help automate the management of Alcatel-Lucent Enterprise AOS network appliances.

This collection has been tested against Alcatel-Lucent Enterprise AOS 8.9R03.

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
[ale.aos.aos](https://github.com/Mathias-gt/ale.aos/blob/main/docs/ale.aos.aos_cliconf.rst)|Use aos cliconf to run command on Alcatel-Lucent Enterprise AOS platform

### Modules
Name | Description
--- | ---
[ale.aos.aos_command](https://github.com/Mathias-gt/ale.aos/blob/main/docs/ale.aos.aos_command_module.rst)|Run arbitrary commands on an Alcatel-Lucent Enterprise AOS device
[ale.aos.aos_config](https://github.com/Mathias-gt/ale.aos/blob/main/docs/ale.aos.aos_config_module.rst)|Manage Alcatel-Lucent Enterprise AOS configuration sections

<!--end collection content-->

Click the ``Content`` button to see the list of content included in this collection.

## Installing this collection

You can install the Alcatel-Lucent Enterprise AOS collection with the Ansible Galaxy CLI:

    git clone https://github.com/Mathias-gt/ale.aos.git
    cd ale.aos
    ansible-galaxy collection install ./ale-aos-1.0.0.tar.gz

## Using this collection


This collection includes [network resource modules](https://docs.ansible.com/ansible/latest/network/user_guide/network_resource_modules.html).

### Using modules from the Alcatel-Lucent Enterprise AOS collection in your playbooks

You can call modules by their Fully Qualified Collection Namespace (FQCN), such as `ale.aos.aos_config`.
The following example task replaces configuration changes in the existing configuration on a Alcatel-Lucent Enterprise AOS network device, using the FQCN:

```yaml
---
  - name: Disable a port.
    ale.aos.aos_config:
      lines:
        - interfaces port 1/1/1 admin-state disable
```

## Release notes

<!--Add a link to a changelog.md file or an external docsite to cover this information. -->

Release notes are available [here](https://github.com/Mathias-gt/ale.aos/blob/main/CHANGELOG.rst).

## More information

- [Ansible network resources](https://docs.ansible.com/ansible/latest/network/getting_started/network_resources.html)
- [Ansible Collection overview](https://github.com/ansible-collections/overview)
- [Ansible User guide](https://docs.ansible.com/ansible/latest/user_guide/index.html)
- [Ansible Developer guide](https://docs.ansible.com/ansible/latest/dev_guide/index.html)
- [Ansible Community code of conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html)

## Licensing

GNU General Public License v3.0 or later.

See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.
