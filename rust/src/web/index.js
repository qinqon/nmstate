import 'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.9/codemirror.min.js';
import 'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.9/mode/yaml/yaml.min.js';

import init, { expand_policy } from './pkg/nmstate_web.js';

const stateEditor = CodeMirror.fromTextArea(document.getElementById('state'), {
    mode: 'yaml',
    lineNumbers: true,
    theme: 'dracula'
});

const policyEditor = CodeMirror.fromTextArea(document.getElementById('policy'), {
    mode: 'yaml',
    lineNumbers: true,
    theme: 'dracula'
});


const expandedEditor = CodeMirror.fromTextArea(document.getElementById('expanded'), {
    mode: 'yaml',
    lineNumbers: true,
    theme: 'dracula'
});

async function run() {
    await init(); // Initialize the WASM module
    stateEditor.setValue(`
routes:
  running:
    - destination: 0.0.0.0/0
      next-hop-address: 192.168.100.1
      next-hop-interface: eth1
      table-id: 254
    - destination: 1.1.1.0/24
      next-hop-address: 192.168.100.1
      next-hop-interface: eth1
      table-id: 254
interfaces:
  - name: eth1
    type: ethernet
    state: up
    mac-address: 00:00:5E:00:00:01
    ipv4:
      address:
        - ip: 10.244.0.1
          prefix-length: 24
        - ip: 169.254.1.0
          prefix-length: 16
      dhcp: true
      enabled: true
        `);

    policyEditor.setValue(`
capture:
  default-gw: routes.running.destination=="0.0.0.0/0"
  base-iface: >-
    interfaces.name==capture.default-gw.routes.running.0.next-hop-interface
desiredState:
  interfaces:
    - name: br1
      description: >-
        DHCP aware Linux bridge to connect a nic that is referenced by a
        default gateway
      type: linux-bridge
      state: up
      mac-address: "{{ capture.base-iface.interfaces.0.mac-address }}"
      ipv4:
        dhcp: true
        enabled: true
      bridge:
        options:
          stp:
            enabled: false
        port:
          - name: "{{ capture.base-iface.interfaces.0.name }}"
    `);
    expandedEditor.setValue(expand_policy (stateEditor.getValue(), policyEditor.getValue()));

    stateEditor.on('change', (instance) => {
        expandedEditor.setValue(expand_policy (stateEditor.getValue(), policyEditor.getValue()));
    });

    policyEditor.on('change', (instance) => {
        expandedEditor.setValue(expand_policy (stateEditor.getValue(), policyEditor.getValue()));
    });


}

run();
