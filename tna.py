import base64
from datetime import timezone
from cashaddress import convert
from bitcoin.core.script import CScriptOp
from blockchain_parser.address import Address
from blockchain_parser.utils import btc_ripemd160, double_sha256
from bitcoin import base58

def to_cash_addr(addr):
    return convert.to_cash_address(addr)[12:] # remove "bitcoincash:" prefix

def extract(block, tx):
    inputs = []
    outputs = []

    if not tx.is_coinbase():
        for input_index, item in enumerate(tx.inputs):
            xput = { "i": input_index }

            for chunk_index, chunk in enumerate(item.script.operations):
                if isinstance(chunk, bytes):
                    op_b = base64.b64encode(chunk).decode("utf-8")

                    if op_b == '': # TODO: special case to match bitd (investigate bitcoinlib)
                        xput["b" + str(chunk_index)] = { "op": 0 }
                    else:
                        xput["b" + str(chunk_index)] = op_b
                        xput["h" + str(chunk_index)] = chunk.hex()
                elif isinstance(chunk, CScriptOp):
                    xput["b" + str(chunk_index)] = { "op": int(chunk) }
                else:
                    if chunk == 1: # TODO: special case to match bitd (investigate bitcoinlib)
                        xput["b" + str(chunk_index)] = { "op": 81 }
                    else:
                        xput["b" + str(chunk_index)] = chunk

            xput["str"] = item.script.value
            sender = {
                "h": item.transaction_hash,
                "i": item.transaction_index,
            }

            addr = None

            if len(item.script.operations) == 2: # p2pk / p2pkh
                a = item.script.operations[1]
                if isinstance(a, str) or isinstance(a, bytes): # could be CScriptOp in rare case
                    if len(a) == 33 or len(a) == 65:
                        addr = Address.from_public_key(a).address

            if addr is None: # p2sh
                version = b'\x05'
                hash160 = btc_ripemd160(item.script.operations[-1])
                checksum = double_sha256(version + hash160)
                addr = base58.encode(version + hash160 + checksum[:4])

            if addr is not None:
                try:
                    sender['a'] = to_cash_addr(addr)
                except:
                    pass

            xput["e"] = sender
            inputs.append(xput)

    for output_index, item in enumerate(tx.outputs):
        xput = { "i": output_index }

        for chunk_index, chunk in enumerate(item.script.operations):
            if isinstance(chunk, bytes):
                xput["b" + str(chunk_index)] = base64.b64encode(chunk).decode("utf-8")
                try:
                    xput["s" + str(chunk_index)] = chunk.decode("utf-8")
                except UnicodeDecodeError:
                    pass
                xput["h" + str(chunk_index)] = chunk.hex()
            elif isinstance(chunk, CScriptOp):
                xput["b" + str(chunk_index)] = { "op": int(chunk) }
            else:
                xput["b" + str(chunk_index)] = chunk

        xput["str"] = item.script.value

        receiver = {
            "v": item.value,
            "i": output_index
        }
        # bitdb only supports single address, so we will too
        addresses = [str(m.address) for m in item.addresses]
        if len(addresses) == 1:
            receiver["a"] = to_cash_addr(addresses[0])
        xput["e"] = receiver

        outputs.append(xput)


    d = {
        "tx": { "h": tx.hash },
        "in": inputs,
        "out": outputs,
    }

    if block is not None:
        d['blk'] = {
            "i": block.height,
            "h": block.hash,
            "t": int(block.header.timestamp.replace(tzinfo=timezone.utc).timestamp())
        }
    return d
