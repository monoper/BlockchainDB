import asyncio


async def foo(n):
    return n + 1

async def main():
    tasks = []

    for i in range(7, 11):
        tasks.append(foo(i))

    result = await asyncio.gather(*tasks)

    print(result)
    return result

res = asyncio.run(main())
print(res)
