#!/bin/bash

# 获取最新提交的sha
commit_sha=$(gh api repos/LZhengg324/SE-Jihub-BackEnd/commits?sha=lz --jq '.[0].sha')

# 检查是否成功获取sha
if [ -z "$commit_sha" ]; then
  echo "Error: Failed to fetch the latest commit SHA."
  exit 1
fi

# 获取最新提交的详细信息并保存到test.txt
gh api repos/LZhengg324/SE-Jihub-BackEnd/commits/$commit_sha --jq '.commit.message' > test.txt

echo "Latest commit details saved to test.txt"
