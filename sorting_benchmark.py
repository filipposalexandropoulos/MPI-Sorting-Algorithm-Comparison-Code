import time
import math
import random
import argparse
from datetime import datetime


INT_RANGE=(0,10_000_000)
FLOAT_RANGE=(0.0,10_000_000.0)


def _gen(n,typ):
    if typ=="integers":
        return [random.randint(*INT_RANGE) for _ in range(n)]
    return [random.uniform(*FLOAT_RANGE) for _ in range(n)]

def _half_sorted(a):
    s=sorted(a)
    mid=len(s)//2
    tail=[random.randint(*INT_RANGE) if isinstance(a[0],int) else random.uniform(*FLOAT_RANGE) for _ in range(len(s)-mid)]
    return s[:mid]+tail

def _partially_sorted(a):
    s=sorted(a)
    n=len(s)
    for _ in range(max(1,n//10)):
        i,j=random.randrange(n),random.randrange(n)
        s[i],s[j]=s[j],s[i]
    return s

def apply_variant(a,variant):
    if variant=="random":       return a
    if variant=="half_sorted":  return _half_sorted(a)
    if variant=="partial_sort": return _partially_sorted(a)
    if variant=="sorted":       return sorted(a)
    if variant=="reversed":     return sorted(a,reverse=True)
    return a

def generate(args):
    if args.mode=="large":
        return [apply_variant(_gen(args.size,args.type),args.variant)]
    lists=[]
    variants=["random","half_sorted","partial_sort","sorted","reversed"]
    for _ in range(args.count):
        lists.append(apply_variant(_gen(args.size,args.type),random.choice(variants)))
    return lists

def write_input(lists,path):
    with open(path,"w") as f:
        f.write(f"LISTS:{len(lists)}\n")
        for lst in lists:
            f.write(" ".join(map(str,lst))+"\n")
    print(f"Input written to '{path}'")


def bubble_sort(arr):
    a=arr[:]
    n=len(a)
    for i in range(n):
        swapped=False
        for j in range(0,n-i-1):
            if a[j]>a[j+1]:
                a[j],a[j+1]=a[j+1],a[j]
                swapped=True
        if not swapped:
            break
    return a

def selection_sort(arr):
    a=arr[:]
    n=len(a)
    for i in range(n):
        min_idx=i
        for j in range(i+1,n):
            if a[j]<a[min_idx]:
                min_idx=j
        a[i],a[min_idx]=a[min_idx],a[i]
    return a

def insertion_sort(arr):
    a=arr[:]
    for i in range(1,len(a)):
        key=a[i]
        j=i-1
        while j>=0 and a[j]>key:
            a[j+1]=a[j]
            j-=1
        a[j+1]=key
    return a

def merge_sort(arr):
    if len(arr)<=1:
        return arr[:]
    mid=len(arr)//2
    return _merge(merge_sort(arr[:mid]),merge_sort(arr[mid:]))

def _merge(left,right):
    result=[]
    i=j=0
    while i<len(left) and j<len(right):
        if left[i]<=right[j]:
            result.append(left[i]); i+=1
        else:
            result.append(right[j]); j+=1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

def quick_sort(arr):
    a=arr[:]
    _qs(a,0,len(a)-1)
    return a

def _qs(a,low,high):
    if low<high:
        pi=_partition(a,low,high)
        _qs(a,low,pi-1)
        _qs(a,pi+1,high)

def _partition(a,low,high):
    mid=(low+high)//2
    if a[mid]<a[low]:   a[low],a[mid]=a[mid],a[low]
    if a[high]<a[low]:  a[low],a[high]=a[high],a[low]
    if a[mid]<a[high]:  a[mid],a[high]=a[high],a[mid]
    pivot=a[high]
    i=low-1
    for j in range(low,high):
        if a[j]<=pivot:
            i+=1
            a[i],a[j]=a[j],a[i]
    a[i+1],a[high]=a[high],a[i+1]
    return i+1

def heap_sort(arr):
    a=arr[:]
    n=len(a)
    for i in range(n//2-1,-1,-1):
        _heapify(a,n,i)
    for i in range(n-1,0,-1):
        a[0],a[i]=a[i],a[0]
        _heapify(a,i,0)
    return a

def _heapify(a,n,i):
    largest=i
    l,r=2*i+1,2*i+2
    if l<n and a[l]>a[largest]: largest=l
    if r<n and a[r]>a[largest]: largest=r
    if largest!=i:
        a[i],a[largest]=a[largest],a[i]
        _heapify(a,n,largest)

def shell_sort(arr):
    a=arr[:]
    n=len(a)
    gap=n//2
    while gap>0:
        for i in range(gap,n):
            temp=a[i]
            j=i
            while j>=gap and a[j-gap]>temp:
                a[j]=a[j-gap]
                j-=gap
            a[j]=temp
        gap//=2
    return a

def counting_sort(arr):
    if not arr or isinstance(arr[0],float):
        return sorted(arr)
    a=arr[:]
    min_val=min(a)
    max_val=max(a)
    if (max_val-min_val)>len(a)*10:
        return sorted(a)
    count=[0]*(max_val-min_val+1)
    for x in a:
        count[x-min_val]+=1
    result=[]
    for i,cnt in enumerate(count):
        result.extend([i+min_val]*cnt)
    return result

def radix_sort(arr):
    if not arr or isinstance(arr[0],float):
        return sorted(arr)
    a=arr[:]
    max_val=max(a)
    exp=1
    while max_val//exp>0:
        a=_radix_pass(a,exp)
        exp*=10
    return a

def _radix_pass(a,exp):
    n=len(a)
    output=[0]*n
    count=[0]*10
    for num in a:
        count[(num//exp)%10]+=1
    for i in range(1,10):
        count[i]+=count[i-1]
    for i in range(n-1,-1,-1):
        idx=(a[i]//exp)%10
        output[count[idx]-1]=a[i]
        count[idx]-=1
    return output

def bucket_sort(arr):
    if not arr:
        return []
    a=arr[:]
    max_val=max(a)
    bucket_count=max(1,int(math.sqrt(len(a))))
    buckets=[[] for _ in range(bucket_count)]
    for x in a:
        idx=min(int(x/(max_val+1)*bucket_count),bucket_count-1)
        buckets[idx].append(x)
    result=[]
    for b in buckets:
        result.extend(sorted(b))
    return result

def tim_sort(arr):
    a=list(arr)
    n=len(a)
    if n<2:
        return a
    MIN_MERGE=32

    def compute_minrun(length):
        r=0
        while length>=2*MIN_MERGE:
            r|=length&1
            length>>=1
        return length+r

    def reverse_in_place(buf,lo,hi):
        hi-=1
        while lo<hi:
            buf[lo],buf[hi]=buf[hi],buf[lo]
            lo+=1
            hi-=1

    def count_run(buf,lo,hi):
        if lo+1==hi:
            return 1
        i=lo+1
        if buf[i]<buf[lo]:
            i+=1
            while i<hi and buf[i]<buf[i-1]:
                i+=1
            reverse_in_place(buf,lo,i)
        else:
            i+=1
            while i<hi and buf[i]>=buf[i-1]:
                i+=1
        return i-lo

    def binary_insertion_sort(buf,lo,hi,start):
        if start==lo:
            start+=1
        while start<hi:
            pivot=buf[start]
            left,right=lo,start
            while left<right:
                mid=(left+right)>>1
                if pivot<buf[mid]:
                    right=mid
                else:
                    left=mid+1
            j=start
            while j>left:
                buf[j]=buf[j-1]
                j-=1
            buf[left]=pivot
            start+=1

    def merge(buf,lo,mid,hi):
        len1,len2=mid-lo,hi-mid
        if len1<=len2:
            left=buf[lo:mid]
            i,j,k=0,mid,lo
            while i<len1 and j<hi:
                if buf[j]<left[i]:
                    buf[k]=buf[j]; j+=1
                else:
                    buf[k]=left[i]; i+=1
                k+=1
            while i<len1:
                buf[k]=left[i]; i+=1; k+=1
        else:
            right=buf[mid:hi]
            i,j,k=mid-1,len2-1,hi-1
            while i>=lo and j>=0:
                if right[j]<buf[i]:
                    buf[k]=buf[i]; i-=1
                else:
                    buf[k]=right[j]; j-=1
                k-=1
            while j>=0:
                buf[k]=right[j]; j-=1; k-=1

    def merge_at(buf,stack,idx):
        base1,len1=stack[idx]
        base2,len2=stack[idx+1]
        merge(buf,base1,base1+len1,base1+len1+len2)
        stack[idx]=(base1,len1+len2)
        if idx==len(stack)-3:
            stack[idx+1]=stack[idx+2]
        stack.pop()

    def merge_collapse(buf,stack):
        while len(stack)>1:
            idx=len(stack)-2
            if (idx>0 and stack[idx-1][1]<=stack[idx][1]+stack[idx+1][1]) or \
               (idx>1 and stack[idx-2][1]<=stack[idx-1][1]+stack[idx][1]):
                if stack[idx-1][1]<stack[idx+1][1]:
                    idx-=1
                merge_at(buf,stack,idx)
            elif stack[idx][1]<=stack[idx+1][1]:
                merge_at(buf,stack,idx)
            else:
                break

    def merge_force_collapse(buf,stack):
        while len(stack)>1:
            idx=len(stack)-2
            if idx>0 and stack[idx-1][1]<stack[idx+1][1]:
                idx-=1
            merge_at(buf,stack,idx)

    minrun=compute_minrun(n)
    stack=[]
    lo=0
    while lo<n:
        run_len=count_run(a,lo,n)
        if run_len<minrun:
            force=min(n-lo,minrun)
            binary_insertion_sort(a,lo,lo+force,lo+run_len)
            run_len=force
        stack.append((lo,run_len))
        merge_collapse(a,stack)
        lo+=run_len
    merge_force_collapse(a,stack)
    return a

def comb_sort(arr):
    a=arr[:]
    n=len(a)
    gap=n
    shrink=1.3
    sorted_=False
    while not sorted_:
        gap=int(gap/shrink)
        if gap<=1:
            gap=1
            sorted_=True
        i=0
        while i+gap<n:
            if a[i]>a[i+gap]:
                a[i],a[i+gap]=a[i+gap],a[i]
                sorted_=False
            i+=1
    return a

def bitonic_sort(arr):
    if not arr:
        return []
    n=len(arr)
    size=1
    while size<n: size<<=1
    INF=max(arr)+1
    a=arr[:]+[INF]*(size-n)
    _bitonic(a,0,size,True)
    return a[:n]

def _bitonic(a,lo,cnt,asc):
    if cnt>1:
        k=cnt//2
        _bitonic(a,lo,k,True)
        _bitonic(a,lo+k,cnt-k,False)
        _bitonic_merge(a,lo,cnt,asc)

def _bitonic_merge(a,lo,cnt,asc):
    if cnt>1:
        k=1
        while k<cnt: k<<=1
        k>>=1
        for i in range(lo,lo+cnt-k):
            if (a[i]>a[i+k])==asc:
                a[i],a[i+k]=a[i+k],a[i]
        _bitonic_merge(a,lo,k,asc)
        _bitonic_merge(a,lo+k,cnt-k,asc)


ALGORITHMS=[
    ("Bubble Sort",    bubble_sort),
    ("Selection Sort", selection_sort),
    ("Insertion Sort", insertion_sort),
    ("Merge Sort",     merge_sort),
    ("Quick Sort",     quick_sort),
    ("Heap Sort",      heap_sort),
    ("Shell Sort",     shell_sort),
    ("Counting Sort",  counting_sort),
    ("Radix Sort",     radix_sort),
    ("Bucket Sort",    bucket_sort),
    ("Tim Sort",       tim_sort),
    ("Comb Sort",      comb_sort),
    ("Bitonic Sort",   bitonic_sort),
]


def benchmark(lists,skip_set):
    totals={name:0.0 for name,_ in ALGORITHMS}
    total=len(lists)
    for i,lst in enumerate(lists):
        print(f"  Sorting list {i+1}/{total}...",end="\r")
        for name,fn in ALGORITHMS:
            if name in skip_set:
                continue
            t0=time.perf_counter()
            fn(lst[:])
            totals[name]+=(time.perf_counter()-t0)
    print()
    return [(name,None if name in skip_set else totals[name]/60) for name,_ in ALGORITHMS]

def write_output(results,output_file):
    with open(output_file,"w") as f:
        f.write(f"{'Algorithm':<24}  Time (min)\n")
        for name,ms in results:
            if ms is None:
                f.write(f"{name:<24}  SKIPPED\n")
            else:
                f.write(f"{name:<24}  {ms:.6f}\n")
    print(f"Results saved to '{output_file}'")

def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=["large","many"],required=True)
    p.add_argument("--type",choices=["integers","floats"],default="integers")
    p.add_argument("--variant",choices=["random","half_sorted","partial_sort","sorted","reversed"],default="random")
    p.add_argument("--size",type=int,default=1_000_000)
    p.add_argument("--count",type=int,default=1_000_000)
    p.add_argument("--seed",type=int,default=42)
    p.add_argument("--input",type=str,default="input.txt")
    p.add_argument("--output",type=str,default="results.txt")
    p.add_argument("--skip",type=str,nargs="+",default=[])
    return p.parse_args()


if __name__=="__main__":
    args=parse_args()
    random.seed(args.seed)

    print("Generating data...")
    lists=generate(args)
    write_input(lists,args.input)

    print("Benchmarking...")
    results=benchmark(lists,set(args.skip))
    write_output(results,args.output)
