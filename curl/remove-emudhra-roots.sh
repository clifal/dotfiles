#!/bin/bash
# /etc/ssl/cert.pem から emSign ECC Root CA - G3 と AAA Certificate Services を外す。
# macOS 付属の curl・git・python3 が鍵の漏えいした eMudhra の中間 CA を信頼しないようにするため。
# 手順は https://emudhra.we-have-a-problem.com/ と https://support.apple.com/en-us/149555 に従う。
# macOS の更新でファイルが戻ることがあるので、更新後に再実行する。
set -euo pipefail

F=/etc/ssl/cert.pem
ROOTS=(
  '=== /C=IN/OU=emSign PKI/O=eMudhra Technologies Limited/CN=emSign ECC Root CA - G3'
  '=== /C=GB/ST=Greater Manchester/L=Salford/O=Comodo CA Limited/CN=AAA Certificate Services'
)

[ -e "$F.orig" ] || sudo cp -p "$F" "$F.orig"
echo "backup: $(ls -l "$F.orig")"

for s in "${ROOTS[@]}"; do
  t=$(mktemp)
  awk -v s="$s" '/^(===|###) /{skip=0} $0==s{skip=1} !skip' "$F" > "$t"
  [ -s "$t" ] && sudo install -m 0644 -o root -g wheel "$t" "$F"
  rm -f "$t"
done

echo "--- remaining (should be empty):"
openssl crl2pkcs7 -nocrl -certfile "$F" | openssl pkcs7 -print_certs -noout |
  grep -E 'emSign ECC Root CA - G3|AAA Certificate Services' || echo "(none)"

echo "--- /usr/bin/curl without ~/.curlrc (expect exit 60):"
for h in dv-g3b dv-g3b-aaa; do
  /usr/bin/curl -q -s -o /dev/null --max-time 20 "https://$h-emudhra.we-have-a-problem.com/" &&
    echo "$h: ACCEPTED (bad)" || echo "$h: rejected (exit $?)"
done
echo "--- sanity check (expect 200):"
/usr/bin/curl -q -s -o /dev/null -w '%{http_code}\n' https://example.com/
