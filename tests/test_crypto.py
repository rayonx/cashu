import pytest

from cashu.core.b_dhke import (
    alice_verify_dleq,
    hash_e,
    hash_to_curve,
    step1_alice,
    step2_bob,
    step2_bob_dleq,
    step3_alice,
)
from cashu.core.secp import PrivateKey, PublicKey


def test_hash_to_curve():
    result = hash_to_curve(
        bytes.fromhex(
            "0000000000000000000000000000000000000000000000000000000000000000"
        )
    )
    assert (
        result.serialize().hex()
        == "0266687aadf862bd776c8fc18b8e9f8e20089714856ee233b3902a591d0d5f2925"
    )

    result = hash_to_curve(
        bytes.fromhex(
            "0000000000000000000000000000000000000000000000000000000000000001"
        )
    )
    assert (
        result.serialize().hex()
        == "02ec4916dd28fc4c10d78e287ca5d9cc51ee1ae73cbfde08c6b37324cbfaac8bc5"
    )


def test_hash_to_curve_iteration():
    """This input causes multiple rounds of the hash_to_curve algorithm."""
    result = hash_to_curve(
        bytes.fromhex(
            "0000000000000000000000000000000000000000000000000000000000000002"
        )
    )
    assert (
        result.serialize().hex()
        == "02076c988b353fcbb748178ecb286bc9d0b4acf474d4ba31ba62334e46c97c416a"
    )


def test_step1():
    """"""
    B_, blinding_factor = step1_alice(
        "test_message",
        blinding_factor=bytes.fromhex(
            "0000000000000000000000000000000000000000000000000000000000000001"
        ),  # 32 bytes
    )

    assert (
        B_.serialize().hex()
        == "02a9acc1e48c25eeeb9289b5031cc57da9fe72f3fe2861d264bdc074209b107ba2"
    )
    assert blinding_factor.private_key == bytes.fromhex(
        "0000000000000000000000000000000000000000000000000000000000000001"
    )


def test_step2():
    B_, _ = step1_alice(
        "test_message",
        blinding_factor=bytes.fromhex(
            "0000000000000000000000000000000000000000000000000000000000000001"
        ),  # 32 bytes
    )
    a = PrivateKey(
        privkey=bytes.fromhex(
            "0000000000000000000000000000000000000000000000000000000000000001"
        ),
        raw=True,
    )
    C_, e, s = step2_bob(B_, a)
    assert (
        C_.serialize().hex()
        == "02a9acc1e48c25eeeb9289b5031cc57da9fe72f3fe2861d264bdc074209b107ba2"
    )


def test_step3():
    # C = C_ - A.mult(r)
    C_ = PublicKey(
        bytes.fromhex(
            "02a9acc1e48c25eeeb9289b5031cc57da9fe72f3fe2861d264bdc074209b107ba2"
        ),
        raw=True,
    )
    r = PrivateKey(
        privkey=bytes.fromhex(
            "0000000000000000000000000000000000000000000000000000000000000001"
        )
    )

    A = PublicKey(
        pubkey=b"\x02"
        + bytes.fromhex(
            "0000000000000000000000000000000000000000000000000000000000000001",
        ),
        raw=True,
    )
    C = step3_alice(C_, r, A)

    assert (
        C.serialize().hex()
        == "03c724d7e6a5443b39ac8acf11f40420adc4f99a02e7cc1b57703d9391f6d129cd"
    )


def test_dleq_hash_e():
    C_ = PublicKey(
        bytes.fromhex(
            "02a9acc1e48c25eeeb9289b5031cc57da9fe72f3fe2861d264bdc074209b107ba2"
        ),
        raw=True,
    )
    K = PublicKey(
        pubkey=b"\x02"
        + bytes.fromhex(
            "0000000000000000000000000000000000000000000000000000000000000001",
        ),
        raw=True,
    )
    R1 = PublicKey(
        pubkey=b"\x02"
        + bytes.fromhex(
            "0000000000000000000000000000000000000000000000000000000000000001",
        ),
        raw=True,
    )
    R2 = PublicKey(
        pubkey=b"\x02"
        + bytes.fromhex(
            "0000000000000000000000000000000000000000000000000000000000000001",
        ),
        raw=True,
    )
    e = hash_e(R1, R2, K, C_)
    assert e.hex() == "a4dc034b74338c28c6bc3ea49731f2a24440fc7c4affc08b31a93fc9fbe6401e"


def test_dleq_step2_bob_dleq():
    B_, _ = step1_alice(
        "test_message",
        blinding_factor=bytes.fromhex(
            "0000000000000000000000000000000000000000000000000000000000000001"
        ),  # 32 bytes
    )
    a = PrivateKey(
        privkey=bytes.fromhex(
            "0000000000000000000000000000000000000000000000000000000000000001"
        ),
        raw=True,
    )
    p_bytes = bytes.fromhex(
        "0000000000000000000000000000000000000000000000000000000000000001"
    )  # 32 bytes
    e, s = step2_bob_dleq(B_, a, p_bytes)
    assert e.hex() == "9818e061ee51d5c8edc3342369a554998ff7b4381c8652d724cdf46429be73d9"
    assert (
        s.hex() == "9818e061ee51d5c8edc3342369a554998ff7b4381c8652d724cdf46429be73da"
    )  # differs from e only in least significant byte because `a = 0x1`

    # change `a`
    a = PrivateKey(
        privkey=bytes.fromhex(
            "0000000000000000000000000000000000000000000000000000000000001111"
        ),
        raw=True,
    )
    e, s = step2_bob_dleq(B_, a, p_bytes)
    assert e.hex() == "df1984d5c22f7e17afe33b8669f02f530f286ae3b00a1978edaf900f4721f65e"
    assert s.hex() == "828404170c86f240c50ae0f5fc17bb6b82612d46b355e046d7cd84b0a3c934a0"


def test_dleq_alice_verify_dleq():
    # e from test_step2_bob_dleq for a=0x1
    e = bytes.fromhex(
        "9818e061ee51d5c8edc3342369a554998ff7b4381c8652d724cdf46429be73d9"
    )
    # s from test_step2_bob_dleq for a=0x1
    s = bytes.fromhex(
        "9818e061ee51d5c8edc3342369a554998ff7b4381c8652d724cdf46429be73da"
    )
    # pubkey of a=0x1
    K = PublicKey(
        bytes.fromhex(
            "0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798",
        ),
        raw=True,
    )

    # B_ is the same as we did:
    # B_, _ = step1_alice(
    #     "test_message",
    #     blinding_factor=bytes.fromhex(
    #         "0000000000000000000000000000000000000000000000000000000000000001"
    #     ),  # 32 bytes
    # )
    B_ = bytes.fromhex(
        "02a9acc1e48c25eeeb9289b5031cc57da9fe72f3fe2861d264bdc074209b107ba2"
    )

    # # C_ is the same as if we did:
    # a = PrivateKey(
    #     privkey=bytes.fromhex(
    #         "0000000000000000000000000000000000000000000000000000000000000001"
    #     ),
    #     raw=True,
    # )
    # C_, e, s = step2_bob(B_, a)

    C_ = bytes.fromhex(
        "02a9acc1e48c25eeeb9289b5031cc57da9fe72f3fe2861d264bdc074209b107ba2"
    )

    assert alice_verify_dleq(e, s, K, B_, C_)

    # ----- test again with B_ and C_ as per step1 and step2

    B_, _ = step1_alice(
        "test_message",
        blinding_factor=bytes.fromhex(
            "0000000000000000000000000000000000000000000000000000000000000001"
        ),  # 32 bytes
    )
    a = PrivateKey(
        privkey=bytes.fromhex(
            "0000000000000000000000000000000000000000000000000000000000000001"
        ),
        raw=True,
    )
    C_, e, s = step2_bob(B_, a)
    assert alice_verify_dleq(e, s, K, B_.serialize(), C_.serialize())
